def insert_chunk_cpt(d, chunk) :
  if not d.has_key(chunk) :
    d[chunk] = 0
  d[chunk] += 1

def ngram_extractor(su, n, *argv) :
  for i in xrange(len(su) - n) :
    chunk = su[i:i+n]
    for d in argv :
      insert_chunk_cpt(d, chunk)

def build_json_filename_output(path_input) :
  root_dir, filename = os.path.split(path_input)
  f = filename.split('.')
  root_filename = '.'.join(f[:-1])
  json_output_filename = '.'.join([root_filename, 'features', f[-1]])
  return json_output_filename



