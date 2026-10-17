"""Pinyin helpers: split Pinyin into syllables, convert tone marks to numbers,
and work out how a phrase is actually spoken (tone changes / sandhi).

A parsed phrase is a list of segments:
  ("syl", base, tone)   base without tone, ü written as "v"; tone 1-4, 5 = neutral
  ("punct", char)       one of , . ! ? :
  ("space", " ")        word boundary (only kept for display)
"""

import re
import unicodedata

# Every syllable the TTS model knows (Baker / Matcha inventory), ü written as v.
SYLLABLES = set("""
a ai an ang ao ba bai ban bang bao bei ben beng bi bian biao bie bin bing bo bu ca cai can cang cao
ce cen ceng cha chai chan chang chao che chen cheng chi chong chou chu chua chuai chuan chuang chui
chun chuo ci cong cou cu cuan cui cun cuo da dai dan dang dao de dei den deng di dia dian diao die
ding diu dong dou du duan dui dun duo e ei en eng er fa fan fang fei fen feng fo fou fu ga gai
gan gang gao ge gei gen geng gong gou gu gua guai guan guang gui gun guo ha hai han hang hao he hei
hen heng hong hou hu hua huai huan huang hui hun huo ji jia jian jiang jiao jie jin jing jiong
jiu ju juan jue jun ka kai kan kang kao ke ken keng kong kou ku kua kuai kuan kuang kui kun kuo la
lai lan lang lao le lei leng li lia lian liang liao lie lin ling liu lo long lou lu luan lun luo lv
lve ma mai man mang mao me mei men meng mi mian miao mie min ming miu mo mou mu na nai nan nang
nao ne nei nen neng ni nian niang niao nie nin ning niu nong nou nu nuan nun nuo nv nve o ou pa pai
pan pang pao pei pen peng pi pian piao pie pin ping po pou pu qi qia qian qiang qiao qie qin qing
qiong qiu qu quan que qun ran rang rao re ren reng ri rong rou ru rua ruan rui run ruo sa sai san
sang sao se sen seng sha shai shan shang shao she shen sheng shi shou shu shua shuai shuan shuang
shui shun shuo si song sou su suan sui sun suo ta tai tan tang tao te teng ti tian tiao tie ting
tong tou tu tuan tui tun tuo wa wai wan wang wei wen weng wo wu xi xia xian xiang xiao xie xin xing
xiong xiu xu xuan xue xun ya yan yang yao ye yi yin ying yo yong you yu yuan yue yun za zai zan
zang zao ze zei zen zeng zha zhai zhan zhang zhao zhe zhen zheng zhi zhong zhou zhu zhua zhuai
zhuan zhuang zhui zhun zhuo zi zong zou zu zuan zui zun zuo
""".split())
# Valid Pinyin syllables the model can't say. Items using them need a "say" override.
SYLLABLES_NOT_IN_MODEL = {"shei", "zhei", "kei", "sei", "cei", "tei", "nen", "dei"} - SYLLABLES
ALL_SYLLABLES = SYLLABLES | SYLLABLES_NOT_IN_MODEL

TONE_MARKS = {"\u0304": 1, "\u0301": 2, "\u030c": 3, "\u0300": 4}
PUNCT = {",": ",", "，": ",", ".": ".", "。": ".", "!": "!", "！": "!",
         "?": "?", "？": "?", ":": ":", "：": ":", ";": ",", "；": ","}
VOWEL_ORDER = "aoeiuv"


def _letters_and_tones(text):
    """Strip tone marks. Returns (letters, tones) where tones[i] is the tone
    mark found on letters[i] (0 if none). ü becomes v."""
    letters, tones = [], []
    for ch in unicodedata.normalize("NFD", text):
        if ch in TONE_MARKS:
            tones[-1] = TONE_MARKS[ch]
        elif ch == "\u0308":  # diaeresis: u + ¨ = ü
            letters[-1] = "v"
        else:
            letters.append(ch.lower())
            tones.append(0)
    return "".join(letters), tones


def _split_word(word):
    """Split a run of letters into syllables (longest match with backtracking)."""
    if not word:
        return []
    for n in range(min(6, len(word)), 0, -1):
        head = word[:n]
        if head in ALL_SYLLABLES:
            rest = _split_word(word[n:])
            if rest is not None:
                return [head] + rest
    return None


def parse(text):
    """Parse Pinyin with tone marks (or a "say" string with tone numbers)."""
    if re.search(r"[a-zü]\d", text, re.I):
        return parse_numbers(text)
    letters, tones = _letters_and_tones(text)
    segments = []
    i = 0
    for m in re.finditer(r"[a-zv]+|\S|\s+", letters):
        chunk = m.group()
        if chunk[0].isspace():
            segments.append(("space", " "))
        elif chunk[0].isalpha():
            parts = _split_word(chunk)
            if parts is None:
                raise ValueError(f"can't split {chunk!r} in {text!r} into Pinyin syllables")
            pos = m.start()
            for p in parts:
                found = [t for t in tones[pos:pos + len(p)] if t]
                segments.append(("syl", p, found[0] if found else 5))
                pos += len(p)
        elif chunk in PUNCT:
            segments.append(("punct", PUNCT[chunk]))
        elif chunk in "'’-":
            segments.append(("space", ""))  # syllable separator, not a word break
        # anything else (/, …, brackets) is ignored
    return segments


def parse_numbers(text):
    """Parse tone-number Pinyin, e.g. "shui2 a5" or "ni3hao3!".
    An un-numbered syllable is neutral."""
    segments = []
    for tok in re.findall(r"[a-züv:]+[1-5]?|[^\sa-züv:\d]|\s+", text.lower()):
        if tok.isspace():
            segments.append(("space", " "))
        elif tok in PUNCT:
            segments.append(("punct", PUNCT[tok]))
        elif tok[0].isalpha():
            base, tone = (tok[:-1], int(tok[-1])) if tok[-1].isdigit() else (tok, 5)
            parts = _split_word(base.replace("ü", "v").replace("u:", "v"))
            if parts is None:
                raise ValueError(f"can't split {base!r} in {text!r}")
            for p in parts[:-1]:
                segments.append(("syl", p, 5))
            segments.append(("syl", parts[-1], tone))
    return segments


def syllables(segments):
    return [(s[1], s[2]) for s in segments if s[0] == "syl"]


def to_numbers(text):
    """'Nǐmen hǎo!' -> 'Ni3men5 hao3!' (keeps spacing, capitals and punctuation)."""
    def convert(m):
        word = m.group()
        nums = "".join(base.replace("v", "ü") + str(tone)
                       for base, tone in syllables(parse(word)))
        return nums[:1].upper() + nums[1:] if word[:1].isupper() else nums
    return re.sub(r"[^\W\d_]+", convert, unicodedata.normalize("NFC", text))


def spoken(segments):
    """Apply the tone changes that happen in speech.

    - 3rd + 3rd: in a run of 3rd tones, all but the last become 2nd
      (nǐ hǎo -> ní hǎo). A neutral tone or punctuation ends the run.
    - bù before a 4th tone becomes bú.
    Changes for yī depend on meaning, so they're written into the data instead.
    """
    out = [list(s) for s in segments]
    syl = [s for s in out if s[0] == "syl"]
    for a, b in zip(syl, syl[1:]):
        if a[1] == "bu" and a[2] == 4 and b[2] == 4:
            a[2] = 2
    # 3rd-tone runs, broken by punctuation or neutral tones
    run = []
    for s in out + [["punct", "."]]:
        if s[0] == "syl" and s[2] == 3:
            run.append(s)
        elif s[0] == "space":
            continue
        else:
            for r in run[:-1]:
                r[2] = 2
            run = []
    return [tuple(s) for s in out]


def tts_tokens(segments):
    """Model tokens for a parsed phrase: 'ni2', 'xie' (neutral), ',' ..."""
    toks = []
    for s in segments:
        if s[0] == "syl":
            if s[1] not in SYLLABLES:
                raise ValueError(f"the TTS model can't say {s[1]!r}; add a \"say\" override")
            toks.append(s[1] + ("" if s[2] == 5 else str(s[2])))
        elif s[0] == "punct":
            toks.append(s[1])
    if not toks or toks[-1] not in {",", ".", "!", "?", ":"}:
        toks.append(".")  # a final punctuation mark gives cleaner, complete tones
    return toks
