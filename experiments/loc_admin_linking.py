import json
from ner.loc_ner import *
import re
import pickle


def build_trie():
    with open('../data/area_code_2024.json', 'r') as fr:
        area_code = json.load(fr)

    admin_linking = AdminNER()

    for data in area_code:
        province = data['name']
        admin_linking.add_entity('province', province, {'province': province, 'level': 1, 'full': True})
        province2 = re.sub(admin_linking.reg_province, '', province)
        if province2:
            admin_linking.add_entity('province', province2, {'province': province, 'level': 1})

        # l2
        for l2 in data['children']:
            city = l2['name']
            if city == '市辖区':
                city = province
            admin_linking.add_entity('city', city, {'province': province, 'city': city, 'level': 2, 'full': True})
            city2 = re.sub(admin_linking.reg_city, '', city)
            if city2:
                admin_linking.add_entity('city', city2, {'province': province, 'city': city, 'level': 2})
            # l3
            for l3 in l2['children']:
                district = l3['name']
                admin_linking.add_entity('district', district,
                                         {'province': province, 'city': city, 'district': district, 'level': 3,
                                          'full': True})
                district2 = re.sub(admin_linking.reg_district, '', district)
                if district2:
                    admin_linking.add_entity('district', district2,
                                             {'province': province, 'city': city, 'district': district, 'level': 3})

    appends = [
        ['台湾省', '台北市'],
        ['台湾省', '高雄市'],
        ['台湾省', '基隆市'],
        ['台湾省', '台中市'],
        ['台湾省', '台南市'],
        ['台湾省', '新北市'],
        ['台湾省', '桃园市'],
        ['台湾省', '宜兰县'],
        ['台湾省', '基隆市'],
        ['台湾省', '新竹市'],
        ['台湾省', '嘉义市'],
        ['香港', '香港'],
        ['澳门', '澳门']
    ]
    for l1, l2 in appends:
        admin_linking.add_entity('province', l1, {'province': l1, 'level': 1, 'full': True})
        l11 = re.sub(admin_linking.reg_province, '', l1)
        if l11:
            admin_linking.add_entity('province', l11, {'province': l1, 'level': 1})
        admin_linking.add_entity('city', l2, {'province': l1, 'city': l2, 'level': 2, 'full': True})
        l22 = re.sub(admin_linking.reg_city, '', l2)
        if l22:
            admin_linking.add_entity('city', l22, {'province': l1, 'city': l2, 'level': 2})

    admin_linking.save('../data/admin_linking.pkl')


def search():
    test_cases = [
        # "#青岛8岁男孩被教练殴打致死 #琦琦爸爸 每天不停歇是因为孩子还没有等来公道，希望更多人关注",
        # "这个鉴定结果孩子是被“多次打击”致创知道了孩子生前是遭受到了怎样恶毒的毒打,手段也是极其恶劣变态,是用钝性物体多次打击致广泛软组织挫伤导致创伤性休克并肺脏脂肪栓塞死亡,看到伤性休克。 报告都不敢想,每当想起就无比痛心, 琦宝苦等一年等来的还白发人送黑发人三代人的合照青岛是失望,si他瞑目...... 比散大:国史个断这也是抢救无效S亡 20分钟后再弄到医院兵,左音无,思 ...9.0次把人已经打S了 9533 既民体肤呼吸1跳骤货20钟......... 20.232.6.18..13i.60..... 青岛市城阳区第三人民医院病历记录页 1x 14:10 天下奇闻大家看看啊!那两个帽子说:史方如果不承认,我们就抓不了她,我们不能冤枉人,你们要是想那个想抓的话,你们得自己找证据.自己去让她自己承认怎么样怎她得有证据,有证人都不行. 么样...反正就是她不承认,我们抓赢关注青岛8岁男孩翟璟琦生命人闪光",
        # "西安雁塔区龙湖雁塔天辰小区4—10101 时隔两个月这个会所还在经营（无证无照）业主反映：该小区为龙湖雁塔天宸别墅区位于芙蓉西路上，自建立之初就明确规定禁止开设会所等商业设施，以保持居住环境的宁静和公共秩序的和谐。然而，这家会所的老板却无视这一规定，擅自开设会所并且在没有获得合法经营许可的情况下运营。会所老板不仅违反了小区规定，还进一步提出了无理要求，即希望物业准许其顾客的车辆进出小区。在物业明确拒绝其要求后，会所老板采取了极端行动。在2024年6月18日，他纠集了20余名不明身份的人员，围堵了物业办公室并辱骂工作人员。他们强行将小区车库封堵，导致业主们的车辆无法正常进出，严重影响了业主的日常生活。此外，这些人员还围堵了小区大门，并在等待警察到来期间不断辱骂和挑衅业主。当警察到达现场后，他们依然没有收敛自己的行为，继续辱骂挑衅。在冲突升级的过程中，小区保安为了保护业主和物业管理人员的人身安全，主动上前阻拦这些人员。 然而，对方在推搡中却殴打了保安，导致了身体伤害。 据说该高端会所未取得任何经营手续和卫生许可等执照，并且人均消费在上千元，相关部门可以进行核查下。这起事件不仅违反了小区的规定和法律，也严重侵犯了业主和物业管理人员的合法权益。会所老板及其纠集的人员应当受到法律的制裁和惩罚。同时，这也提醒我们，在维护自身权益的同时，也要遵守法律法规和社会公德，共同营造一个和谐、安全、有序的居住环境。",
        'news_ocr 深圳租客陈女士说自己租了一个89平方的房子退租的时候把房间打扫干净了我拍你的手但是押金却被房东扣下了 50多岁左右还请了一个验房师来验房最后最后那個用手电筒对着房间的墙门家具都仔细的查验了一番只要稍微有一点划痕跟我们也有关系就拿张纸做标记可能是我也不知道这真是离谱他妈给离谱开门深圳租房再遇“提燈定損” 租客因租江西房東 COLIOE 民警来到现场以后也是一脸懵第一次遇到这种情况了解情况以后也是看不下去了说这些都是小问题社区物业也做了调节这不就是江西上饶的翻版吗都会有使用痕迹那就供起来真不行就走法律程序第一条提灯定损现在处理的怎么样了不仅未见拆除迹象打卡玉山网红景点 2024年8月13日这栋楼反而成了知名的网红楼还有人居住在里面你看吧当坏人得不到制裁的时候就会有越来越多的人效仿对此大家怎么看',
        'news_ocr 视频字幕OCR 公电小:产中小:主产中县 1人 1/切单我年全多你家车币商公安局公安通黄第点: 手有3法,电点:2000时间: 上市公公局局福体长天然被警察叔叔警告的城市这个打车后排不系安全带再见了上海',
        'news_ocr 可怜的孩子,心痛!! 刚开学出现这种事家长和学生11人死亡,24人受伤平县须昌路丁字路口时,失控造成路边故,一公交司机接送学生的车辆行至东东平县佛山中学门口发生一起交通事 2024年9月3日上午7时27分,山东泰安',
    ]
    admin_linking = AdminNER()
    admin_linking.load('../data/admin_linking.pkl')

    for text in test_cases:
        print('-' * 10)
        print(text)
        # res = admin_linking.exact_parse_text(text)
        res, matchs = admin_linking.parse(text, pos=False)
        for r in matchs:
            print(r)
        print('select:', res)
        print()

        res, matchs = admin_linking.parse(text, pos=True)
        for r in matchs:
            print(r)
        print('select:', res)
        print()
        res = admin_linking.parse2(text)
        print('select:', res)


def parse_json_str(a):
    try:
        return json.loads(a)
    except:
        a = a.replace("'", '"')
        try:
            return json.loads(a)
        except:
            return []


def clean_content(text):
    # 2024.08.16鹤壁市被非法拘禁 “他说去卖房子后来就联系不上他了” 有十九日帮忙抖音搜索小莉河南广播电视台...
    reg = '\\d{4}\\.\\d{1,2}\\.\\d{1,2}.*?(\\.\\.\\.)'
    text = re.sub(reg, '', text)
    return text


def exp_opinion():
    with open('/Users/4paradigm/data/dev/data.json', 'r') as fr:
        data = json.load(fr)
    label_keys = [
        'province', 'city', 'district', 'isChina'
    ]
    # text_keys = ['news_title', 'news_digest', 'news_content']
    text_keys = ['news_title', 'news_ocr', 'news_digest', 'news_content']
    p1, p2, p3 = 0, 0, 0
    n = 0

    admin_linking = AdminNER()
    admin_linking.load('../data/admin_linking.pkl')

    reg_foreign = '(国外|美国|法国|英国|俄罗斯|意大利|以色列|巴西|德国|马来西亚|新加坡|泰国|菲律宾|墨西哥|印度|土耳其|埃及|南非|肯尼亚|摩洛哥|埃塞俄比亚)'
    special_city = ['北京市', '上海市', '重庆市', '天津市']
    reg_tag = '#+(.*?)(#|\\s+|$)'

    description_title_list = [
        ('media_name', '发布者昵称'),
        ('news_title', '新闻标题'),
        ('news_digest', '新闻摘要'),
        ('news_content', '新闻内容'),
        ('news_author', '发布者昵称'),
        ('news_origin_title', '信息源新闻标题'),
        ('news_origin_content', '信息源新闻内容'),
        ('news_origin_author_name', '信息源发布者昵称'),
        ('news_ocr', '视频字幕OCR'),
        ('media_province', '发布者所属省份'),
        ('media_city', '发布者所属城市'),
        ('platform_city', '平台所属城市'),
        ('news_position', '发布文章位置'),
        # ('news_content_ip_location', '文章ip属地'),
    ]

    for d in data:
        n += 1

        label = {k: d[k] for k in label_keys}
        news_content_location = d['news_content_location']

        if '品过 9月16日,山东济宁。网友发视频称, ' in d['news_ocr']:
            print()

        res = {
            'province': None,
            'city': None,
            'district': None,
            'isChina': True
        }
        # news_content_province = parse_json_str(d['news_content_province'])
        # news_content_city = parse_json_str(d['news_content_city'])
        # news_content_county = parse_json_str(d['news_content_county'])
        # if news_content_province:
        #     res['province'] = news_content_province[0]
        # if news_content_city:
        #     res['city'] = news_content_city[0]

        # #认知#崂山路虎女#内容过于真实
        tags = []
        for k in text_keys:
            text = d[k]
            for m in re.finditer(reg_tag, text):
                t = m.group().strip()
                if t:
                    tags.append(t)
        if tags:
            for text in tags:
                link, _ = admin_linking.parse(text)
                if link:
                    res['province'] = link['province']
                    res['city'] = link.get('city', '')
                    res['district'] = link.get('district', '')
                    res['isChina'] = True
                    break

        text_set = set()
        for k in text_keys:
            text = d[k]
            # text = clean_content(d[k])
            if text not in text_set:
                text_set.add(text)
                # link, _ = admin_linking.parse(text, pos=True)
                link = admin_linking.parse2(text)
                if link:
                    if res['province'] and link['province'] != res['province']:
                        continue
                    if res['city'] and link.get('city', '') != res['city']:
                        continue
                    res['province'] = link['province']
                    res['city'] = link.get('city', '')
                    res['district'] = link.get('district', '')
                    res['isChina'] = True
                    break
        if not res['province']:
            for k in text_keys:
                text = d[k]
                m = re.search(reg_foreign, text)
                if m:
                    res['province'] = m.group()
                    break
            res['isChina'] = False

        for k in ['province', 'city', 'district']:
            if not res[k]:
                res[k] = None
        if res['city'] in special_city:
            res['city'] = None
        if res['district'] and res['district'].endswith('市'):
            res['city'] = res['district']
        correct = True

        if res['province'] == label['province']:
            p1 += 1
        else:
            correct = False
        if res['city'] == label['city']:
            p2 += 1
        else:
            correct = False
        if res['isChina'] == label['isChina']:
            p3 += 1
        else:
            correct = False

        if not correct:
            print('-' * 20)
            text_set = set()
            for k in text_keys:
                t = d[k]
                if t not in text_set:
                    text_set.add(t)
                    print(k, t)
                    link, matches = admin_linking.parse(t, pos=True)
                    print('link:', link)
                    print('matches:', matches)

            for k, v in description_title_list:
                print(k, v, d[k])

            d_str = d.copy()
            d_str.pop('province')
            d_str.pop('city')
            d_str.pop('district')
            d_str.pop('news_content_province')
            d_str.pop('news_content_city')
            d_str.pop('news_content_county')
            d_str = str(d_str)
            if label['province']:
                label_prov = re.sub(admin_linking.reg_province, '', label['province'])
                if label_prov in d_str:
                    idx = d_str.index(label_prov)
                    print('prov hit:', d_str[max(0, idx - 50): idx + 20])
            if label['city']:
                label_city = re.sub(admin_linking.reg_city, '', label['city'])
                if label_city in d_str:
                    idx = d_str.index(label_city)
                    print('city hit:', d_str[max(0, idx - 50): idx + 20])
            if label['district']:
                label_district = re.sub(admin_linking.reg_district, '', label['district'])
                if label_district in d_str:
                    idx = d_str.index(label_district)
                    print('district hit:', d_str[max(0, idx - 50): idx + 20])
            print('news_content_location:', news_content_location)
            print('label:', label)
            print('res:', res)
            print()

    print('province:', p1, p1 / n)
    print('city:', p2, p2 / n)
    print('isChina:', p3, p3 / n)


if __name__ == '__main__':
    # build_trie()
    # search()
    exp_opinion()
