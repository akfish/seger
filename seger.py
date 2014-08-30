import json
import urllib, urllib2
import csv
import pylibmc as memcache
import math

_CORPUS_PATH = 'corpus.csv'


POSTAG_ID_UNKNOW = 0
POSTAG_ID_A      = 10
POSTAG_ID_B      = 20
POSTAG_ID_C      = 30
POSTAG_ID_C_N    = 31
POSTAG_ID_C_Z    = 32
POSTAG_ID_D      = 40
POSTAG_ID_D_B    = 41
POSTAG_ID_D_M    = 42
POSTAG_ID_E      = 50
POSTAG_ID_F      = 60
POSTAG_ID_F_S    = 61
POSTAG_ID_F_N    = 62
POSTAG_ID_F_V    = 63
POSTAG_ID_F_Z    = 64
POSTAG_ID_H      = 70
POSTAG_ID_H_M    = 71
POSTAG_ID_H_T    = 72
POSTAG_ID_H_NR   = 73
POSTAG_ID_H_N    = 74
POSTAG_ID_K      = 80
POSTAG_ID_K_M    = 81
POSTAG_ID_K_T    = 82
POSTAG_ID_K_N    = 83
POSTAG_ID_K_S    = 84
POSTAG_ID_K_Z    = 85
POSTAG_ID_K_NT   = 86
POSTAG_ID_K_NS   = 87
POSTAG_ID_M      = 90
POSTAG_ID_N      = 95
POSTAG_ID_N_RZ   = 96
POSTAG_ID_N_T    = 97
POSTAG_ID_N_TA   = 98
POSTAG_ID_N_TZ   = 99
POSTAG_ID_N_Z    = 100
POSTAG_ID_NS     = 101
POSTAG_ID_NS_Z   = 102
POSTAG_ID_N_M    = 103
POSTAG_ID_N_RB   = 104
POSTAG_ID_O      = 107
POSTAG_ID_P      = 108
POSTAG_ID_Q      = 110
POSTAG_ID_Q_V    = 111
POSTAG_ID_Q_T    = 112
POSTAG_ID_Q_H    = 113
POSTAG_ID_R      = 120
POSTAG_ID_R_D    = 121
POSTAG_ID_R_M    = 122
POSTAG_ID_R_N    = 123
POSTAG_ID_R_S    = 124
POSTAG_ID_R_T    = 125
POSTAG_ID_R_Z    = 126
POSTAG_ID_R_B    = 127
POSTAG_ID_S      = 130
POSTAG_ID_S_Z    = 131
POSTAG_ID_T      = 132
POSTAG_ID_T_Z    = 133
POSTAG_ID_U      = 140
POSTAG_ID_U_N    = 141
POSTAG_ID_U_D    = 142
POSTAG_ID_U_C    = 143
POSTAG_ID_U_Z    = 144
POSTAG_ID_U_S    = 145
POSTAG_ID_U_SO   = 146
POSTAG_ID_W      = 150
POSTAG_ID_W_D    = 151
POSTAG_ID_W_SP   = 152
POSTAG_ID_W_S    = 153
POSTAG_ID_W_L    = 154
POSTAG_ID_W_R    = 155
POSTAG_ID_W_H    = 156
POSTAG_ID_Y      = 160
POSTAG_ID_V      = 170
POSTAG_ID_V_O    = 171
POSTAG_ID_V_E    = 172
POSTAG_ID_V_SH   = 173
POSTAG_ID_V_YO   = 174
POSTAG_ID_V_Q    = 175
POSTAG_ID_V_A    = 176
POSTAG_ID_Z      = 180
POSTAG_ID_X      = 190
POSTAG_ID_X_N    = 191
POSTAG_ID_X_V    = 192
POSTAG_ID_X_S    = 193
POSTAG_ID_X_T    = 194
POSTAG_ID_X_Z    = 195
POSTAG_ID_X_B    = 196
POSTAG_ID_SP     = 200
POSTAG_ID_MQ     = 201
POSTAG_ID_RQ     = 202
POSTAG_ID_AD     = 210
POSTAG_ID_AN     = 211
POSTAG_ID_VD     = 212
POSTAG_ID_VN     = 213
POSTAG_ID_SPACE  = 230

mc = {}#memcache.Client()
rows = []
def _load_corpus():

  cached = mc.get('CORPUS_FLAG')
  if cached:
    print "Already cached"
    return
  print "Caching..."

  c = 0
  with open(_CORPUS_PATH, 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
      rows.append(row)
      mc[row[1].decode('gbk')] = float(row[5]) / 100
      #mc.set(row[1], row[5])
      c += 1

  print "Total %d cached" % (c)
  mc["CORPUS_FLAG"] = True
  #mc.set("CORPUS_FLAG", True)
  return

def _parse_query(query):
  kvs = [pair.split('=') for pair in query.split('&')]
  d = {}
  for kv in kvs:
    if len(kv) == 2:
      d[kv[0]] = kv[1]
  return d

_SEGMENT_BASE_URL = 'http://segment.sae.sina.com.cn/urlclient.php'

def _segement(text):
  if not text or text == '':
    return []
  payload = urllib.urlencode([('context', urllib.unquote(text))])
  args = urllib.urlencode([('word_tag', 1), ('encoding', 'UTF-8'),])
  url = _SEGMENT_BASE_URL + '?' + args
  result = urllib2.urlopen(url, payload).read()
  #result = '[{"word_tag": "95", "word": "\u793e\u4f1a\u5b66", "index": "0"}, {"word_tag": "173", "word": "\u662f", "index": "1"}, {"word_tag": "123", "word": "\u4ec0\u4e48", "index": "2"}]'
  #result = unicode(result).encode('utf-8')
  return json.loads(result, parse_int = True, parse_float = True)

_CORPUS_N = 20000000
def _tf_idf(words):
  LF = {}
  for word in words:
    w = word.get('word')
    word['word_tag'] = int(word['word_tag'])
    f = mc.get(w, 0)
    word['gf'] = f
    if not LF.get(w):
      LF[w] = 0
    LF[w] += 1

    idf = 0
    if f == 0:
      idf = math.log(_CORPUS_N)
    else:
      idf = math.log(1 / f)
    word['idf'] = idf

  n = float(len(words))
  for word in words:
    w = word.get('word')
    count = LF[w]
    tf = word['lf'] = count / n
    word['tf_idf'] = tf * word['idf']
  return words

_NV = [
  POSTAG_ID_N,
  POSTAG_ID_N_RZ,
  POSTAG_ID_N_T,
  POSTAG_ID_N_TZ,
  POSTAG_ID_N_Z,
  POSTAG_ID_NS,
  POSTAG_ID_NS_Z,
  POSTAG_ID_V,
  POSTAG_ID_V_O,
  POSTAG_ID_V_E,
  POSTAG_ID_AN,
  POSTAG_ID_VN
  ]
_AD = [
  POSTAG_ID_A,
  POSTAG_ID_D,
  POSTAG_ID_AD,
  POSTAG_ID_VD
  ]

def _extract_keys(words, is_short = False, max_count = 10):
  filtered = []
  # Filter by word tag and add weight information
  for word in words:
    tag = word['word_tag']
    tf_idf = word['tf_idf']
    if tag in _NV:
      word['w'] = 0.8
      word['x'] = tf_idf * word['w']
      filtered.append(word)
    elif tag in _AD:
      word['w'] = 0.6
      word['x'] = tf_idf * word['w']
      filtered.append(word)
  # Kill duplicates
  d = {word['word']: word for word in filtered}
  # Sort
  s = sorted(d.values(), key = lambda word: word['x'], reverse = True)
  def make_key(word):
    if is_short:
      return word['word']
    w = {}
    for key in ['word', 'index', 'word_tag']:
      w[key] = word[key]
    w['x'] = word['tf_idf'] * word['w']
    return w
  keys = [make_key(w) for w in s][0: max_count]
  return keys

def run(query):
  result = {}
  try:
    params = _parse_query(query)
    _load_corpus()
    words = _segement(params.get('c'))
    words = _tf_idf(words)
    result['words'] = words#_encode(words)
    result['keywords'] = _extract_keys(words, bool(params.get('short', False)), int(params.get('max', 10)))
  except Exception as e:
    result['error'] = str(e)

  #print result.get('keywords')
  j = json.dumps(result, ensure_ascii = False).encode('utf-8')
  cb = params.get('callback')
  # JSONP
  if cb:
    j = cb + '(' + j + ')'
  return j
