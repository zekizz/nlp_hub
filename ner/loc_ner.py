"""
行政区划基于词典的entity linking
"""
import re

import ahocorasick
import pickle
from collections import defaultdict
import copy


class NERDict:

    def __init__(self):
        pass

    def load(self, path):
        """加载已经构建好的trie"""
        pass

    def build(self, entity_info_list):
        pass

    def parse(self, text):
        pass


class AdminNER:

    def __init__(self):
        # l4歧义太大，不启用
        self.trie = {
            'province': ahocorasick.Automaton(),
            'city': ahocorasick.Automaton(),
            'district': ahocorasick.Automaton(),
        }
        self.reg_province = '(省|市|(壮族|回族|维吾尔)?自治区)$'
        self.reg_city = '(市|盟|地区|林区|土家族苗族自治州|藏族羌族自治州|彝族自治州|布依族苗族自治州|白族自治州|傣族自治州|傈僳族自治州|藏族自治州|蒙古族藏族自治州|回族自治州|蒙古自治州)$'
        self.reg_district = '(县|区|市|地区)$'
        bad_words = ['公安', '城区', '老城', '新城', '开发', '高新', '服务', '古城', '上高']
        self.reg_bad_words = '^' + '(' + '|'.join(bad_words) + ')'
        self.bad_postfix = '^(大道|大厦|商厦)'
        self.refer = ""

    def add_entity(self, entity_type, k, v):
        if re.search(self.reg_bad_words, k) or re.search(self.reg_bad_words + self.reg_district, k):
            return
        vv = self.trie[entity_type].get(k, None)
        if vv:
            vv.append(v)
        else:
            vv = [v]
        self.trie[entity_type].add_word(k, vv)

    def save(self, path):
        with open(path, 'wb') as fw:
            pickle.dump(self.trie, fw)

    def load(self, path):
        with open(path, 'rb') as fr:
            self.trie = pickle.load(fr)

    def exact_search(self, text):
        res = self.trie['province'].get(text, [])
        if res:
            return 1, copy.deepcopy(res)
        res = self.trie['city'].get(text, [])
        if res:
            return 2, copy.deepcopy(res)
        res = self.trie['district'].get(text, [])
        if res:
            return 3, copy.deepcopy(res)
        return 0, []

    def exact_parse_text(self, text):
        """
        长找断
        """
        result = []
        start = 0
        while start < len(text) - 1:
            matches = []
            for end in range(start + 2, len(text)):
                cur = text[start:end]
                level, res = self.exact_search(cur)
                if res and not re.search(self.bad_postfix, text[end:end + 5]):
                    if level == 3 and self.refer and cur not in self.refer:
                        continue
                    matches.append((cur, len(cur), res))
            matches = sorted(matches, key=lambda x: x[1], reverse=True)
            if matches:
                longest = matches[0][1]
                cur_match = {
                    'start': start,
                    'mention': text[start:start + longest],
                    'entity': []
                }
                for m in matches:
                    if m[1] == longest:
                        cur_match['entity'].extend(m[2])
                result.append(cur_match)
                start += longest
            else:
                start += 1
        return result

    def parse(self, text, exact=True, pos=True, refer=""):
        self.refer = refer
        mention_link = self.exact_parse_text(text)
        if not mention_link:
            return {}, []
        match_province = defaultdict(int)
        match_city = defaultdict(int)
        for item in mention_link:
            entity = sorted(item['entity'], key=lambda x: x['level'])
            clean = []
            for e in entity:
                if e['level'] == entity[0]['level']:
                    clean.append(e)
                    p, c = e.get('province', ''), e.get('city', '')
                    if p:
                        match_province[p] += 1
                    if c:
                        match_city[c] += 1
            item['entity'] = entity

        match_items = []
        for mention in mention_link:
            for item in mention['entity']:
                score = 0
                if item['level'] == 3:
                    flag = False
                    if re.search('[区市县]$', mention['mention']):
                        flag = True
                    if item.get('full', False):
                        score += 12 if flag else 2
                    else:
                        score += 11 if flag else 1
                elif item['level'] == 2:
                    if item.get('full', False):
                        score += 10
                    else:
                        score += 9
                elif item['level'] == 1:
                    if item.get('full', False):
                        score += 5
                    else:
                        score += 4
                score += match_province[item['province']]
                score += match_city.get(item.get('city', ''), 0)
                item['score'] = score
                item['start'] = mention['start']
                item['mention'] = mention['mention']
                match_items.append(item)
        if pos:
            match_items = sorted(match_items, key=lambda x: x['start'])
            tp = []
            for item in match_items:
                if item['level'] >= match_items[0]['level'] and item['province'] == match_items[0]['province']:
                    # if item['level'] <= match_items[0]['level']:
                    if match_items[0]['level'] == 2 and item['city'] != match_items[0]['city']:
                        continue
                    tp.append(item)
            match_items = tp

        if pos:
            match_items = sorted(match_items, key=lambda x: x['score'] - x['start'] / 10, reverse=True)
        else:
            match_items = sorted(match_items, key=lambda x: x['score'], reverse=True)

        selected = match_items[0]
        if selected['level'] == 3:
            return selected, match_items
        for item in match_items[1:]:
            if item['level'] > selected['level'] and item['province'] == selected['province']:
                if selected['level'] >= 2 and item['city'] != selected['city']:
                    continue
                selected = item
        return selected, match_items

    def parse2(self, text):
        link1, _ = self.parse(text, pos=True)
        link2, _ = self.parse(text, pos=False)
        if not link1:
            return {}
        if link1['province'] == link2['province']:
            city1 = link1.get('city', '')
            city2 = link2.get('city', '')
            if not city1 and city2:
                link1['city'] = city2
        if link1['start'] < link2['start'] - 10:
            res = link1
        else:
            res = link2

        return res


class Processor:

    def __init__(self):
        admin_linking = AdminNER()
        admin_linking.load('admin_linking.pkl')
        self.admin_linking = admin_linking
        self.reg_foreign = '(国外|美国|法国|英国|俄罗斯|意大利|以色列|巴西|德国|马来西亚|新加坡|泰国|菲律宾|墨西哥|印度|土耳其|埃及|南非|肯尼亚|摩洛哥|埃塞俄比亚)'
        self.special_city = ['北京市', '上海市', '重庆市', '天津市']
        self.reg_tag = '#+(.{2,10})(#|\\s+|$)'
        self.text_keys = ['news_title', 'news_ocr', 'news_digest', 'news_content']

    def parse(self, d):
        res = {
            'province': None,
            'city': None,
            'district': None,
            'isChina': True
        }
        news_content_location = d['news_content_location']
        if not news_content_location:
            news_content_location = ''
        news_content_location_link, _ = self.admin_linking.parse(news_content_location, pos=True,
                                                                 refer=news_content_location)

        # #认知#崂山路虎女#内容过于真实
        tags = []
        for k in self.text_keys:
            text = d[k]
            for m in re.finditer(self.reg_tag, text):
                t = m.group().strip()
                if t:
                    tags.append(t)
        if tags:
            for text in tags:
                link, _ = self.admin_linking.parse(text)
                if link:
                    res['province'] = link['province']
                    res['city'] = link.get('city', '')
                    res['district'] = link.get('district', '')
                    res['isChina'] = True
                    break

        text_set = set()
        for k in self.text_keys:
            text = d[k]
            # text = clean_content(d[k])
            if text not in text_set:
                text_set.add(text)
                link, _ = self.admin_linking.parse(text, pos=True, refer=news_content_location)
                # link = admin_linking.parse2(text)
                if link:
                    if res['province'] and link['province'] != res['province']:
                        continue
                    if res['city'] and link.get('city', '') != res['city']:
                        continue
                    res['province'] = link['province']
                    res['city'] = link.get('city', '')
                    res['district'] = link.get('district', '')
                    res['isChina'] = True
                    m = re.search(self.reg_foreign, text)
                    if m and m.start() < link['start']:
                        res = {
                            'province': m.group(),
                            'city': None,
                            'district': None,
                            'isChina': False
                        }

        if not res['province']:
            for k in self.text_keys:
                text = d[k]
                m = re.search(self.reg_foreign, text)
                if m:
                    res['province'] = m.group()
                    break
            res['isChina'] = False
            if not res['province']:

                if news_content_location_link:
                    link = news_content_location_link
                    res['province'] = link['province']
                    res['city'] = link.get('city', '')
                    res['district'] = link.get('district', '')
                    res['isChina'] = True
                else:
                    if d['media_city'] or d['media_province']:
                        res['isChina'] = True

        if news_content_location_link and res['province'] == news_content_location_link['province']:
            if not res['city'] and news_content_location_link.get('city', ''):
                res['city'] = news_content_location_link['city']

        for k in ['province', 'city', 'district']:
            if not res[k]:
                res[k] = None
        if res['city'] in self.special_city:
            res['city'] = None
        if res['district'] and res['district'].endswith('市'):
            res['city'] = res['district']

        return res

