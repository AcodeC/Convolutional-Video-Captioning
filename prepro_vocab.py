import re
import json
import argparse
import numpy as np
'''
This file is for data preprocessing

'''

def build_vocab(vids):
    count_thr = 1#params['word_count_threshold']
    # count up the number of words
    counts = {}
    for vid, caps in vids.items():
        for cap in caps['captions']:
            ws = re.sub(r'[.!,;?]', ' ', cap).split()
            for w in ws:
                counts[w] = counts.get(w, 0) + 1
    # cw = sorted([(count, w) for w, count in counts.items()], reverse=True)
    total_words = sum(counts.values())
    bad_words = [w for w, n in counts.items() if n <= count_thr]
    vocab = [w for w, n in counts.items() if n > count_thr]
    bad_count = sum(counts[w] for w in bad_words)
    print('number of bad words: %d/%d = %.2f%%' %
          (len(bad_words), len(counts), len(bad_words) * 100.0 / len(counts)))
    print('number of words in vocab would be %d' % (len(vocab), ))
    print('number of UNKs: %d/%d = %.2f%%' %
          (bad_count, total_words, bad_count * 100.0 / total_words))
    # lets now produce the final annotations
    if bad_count > 0:
        # additional special UNK token we will use below to map infrequent words to
        print('inserting the special UNK token')
        vocab.append('<UNK>')
    for vid, caps in vids.items():
        
        caps = caps['captions']
        vids[vid]['final_captions'] = []
        for cap in caps:
            ws = re.sub(r'[.!,;?]', ' ', cap).split()
            caption = [
                '<sos>'] + [w if counts.get(w, 0) > count_thr else '<UNK>' for w in ws] + ['<eos>']
            vids[vid]['final_captions'].append(caption)
    
    return vocab


def main(params):
    videos = json.load(open(params['input_json'], 'r'))['sentences']
    test_videos=json.load(open(params['test_input_json'], 'r'))['sentences']
    # print(test_videos[1])
    # print(videos[1])
    # videos=videos.extend(test_videos)
    # for i in test_videos:
    #     videos=videos.extend(i)
    
    video_caption = {}
    j=0
    for i in videos:
        j+=1
        print(i)
        if i['video_id'] not in video_caption.keys():
            video_caption[i['video_id']] = {'captions': []}
        video_caption[i['video_id']]['captions'].append(i['caption'])
    for i in test_videos:
        j+=1
        print(i)
        if i['video_id'] not in video_caption.keys():
            video_caption[i['video_id']] = {'captions': []}
        video_caption[i['video_id']]['captions'].append(i['caption'])

    # create the vocab
    vocab = build_vocab(video_caption)
    print(len(vocab))
    itow = {i + 2: w for i, w in enumerate(vocab)}
    wtoi = {w: i + 2 for i, w in enumerate(vocab)}  # inverse table
    wtoi['<eos>'] = 0
    itow[0] = '<eos>'
    wtoi['<sos>'] = 1
    itow[1] = '<sos>'

    out = {}
    out['ix_to_word'] = itow
    out['word_to_ix'] = wtoi
    out['videos'] = {'train': [], 'val': [], 'test': []}
    videos = json.load(open(params['input_json'], 'r'))['videos']
    test_videos=json.load(open(params['test_input_json'], 'r'))['videos']
    for i in videos:
        print(i['id'])
        print(str(i['split'][:3]))
        if str(i['split'])=="validate":
            out['videos'][i['split'][:3]].append(int(i['id']))
        else :
            out['videos'][i['split']].append(int(i['id']))
        print("out"+str(i['id']))
        
    for i in test_videos:
        print(i['id'])
        print(str(i['split'][:3]))
        if str(i['split'])=="validate":
            out['videos'][i['split'][:3]].append(int(i['id']))
        else :
            out['videos'][i['split']].append(int(i['id']))
        print("out"+str(i['id']))
    
    json.dump(out, open(params['info_json'], 'w'))
    json.dump(video_caption, open(params['caption_json'], 'w'))
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # input json
    parser.add_argument('--input_json', type=str, default='data/train_val_videodatainfo.json',
                        help='msr_vtt videoinfo json')

    parser.add_argument('--test_input_json',type=str,default='data/test_videodatainfo.json',
                        help='msrvtt_test')
    parser.add_argument('--info_json', default='data/info.json',
                        help='info about iw2word and word2ix')
    parser.add_argument('--caption_json', default='data/caption.json', help='caption json file')


    parser.add_argument('--word_count_threshold', default=1, type=int,
                        help='only words that occur more than this number of times will be put in vocab')

    args = parser.parse_args()
    params = vars(args)  # convert to ordinary dict
    main(params)