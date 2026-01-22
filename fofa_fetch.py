import os
import re
import requests
import time
import subprocess
import sys
from pathlib import Path

# ===============================
# 配置区
FOFA_URLS = {
    "https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjb3VudHJ5PSJDTiI%3D": "ip.txt",
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0"
}

COUNTER_FILE = "计数.txt"
IP_DIR = "ip"
RTP_DIR = "rtp"
ZUBO_FILE = "zubo.txt"
IPTV_FILE = "IPTV.txt"

# ===============================
# 分类与映射配置
CHANNEL_CATEGORIES = {
    "央视频道": [
        "CCTV1", "CCTV2", "CCTV3", "CCTV4", "CCTV4欧洲", "CCTV4美洲", "CCTV5", "CCTV5+", "CCTV6", "CCTV7",
        "CCTV8", "CCTV9", "CCTV10", "CCTV11", "CCTV12", "CCTV13", "CCTV14", "CCTV15", "CCTV16", "CCTV17", "CCTV4K", "CCTV8K",
        "兵器科技", "风云音乐", "风云足球", "风云剧场", "怀旧剧场", "第一剧场", "女性时尚", "世界地理", "央视台球", "高尔夫网球",
        "央视文化精品", "卫生健康", "电视指南"
    ],
    "卫视频道": [
        "湖南卫视", "浙江卫视", "江苏卫视", "东方卫视", "深圳卫视", "北京卫视", "广东卫视", "广西卫视", "东南卫视", "海南卫视",
        "河北卫视", "河南卫视", "湖北卫视", "江西卫视", "四川卫视", "重庆卫视", "贵州卫视", "云南卫视", "天津卫视", "安徽卫视",
        "山东卫视", "辽宁卫视", "黑龙江卫视", "吉林卫视", "内蒙古卫视", "宁夏卫视", "山西卫视", "陕西卫视", "甘肃卫视", "青海卫视",
        "新疆卫视", "西藏卫视", "三沙卫视", "兵团卫视", "延边卫视", "安多卫视", "康巴卫视", "农林卫视", "山东教育卫视",
        "中国教育1台", "中国教育2台", "中国教育3台", "中国教育4台", "早期教育"
    ],
    "数字频道": [
        "CHC动作电影", "CHC家庭影院", "CHC影迷电影", "淘电影", "淘精彩", "淘剧场", "淘4K", "淘娱乐", "淘BABY", "淘萌宠", "重温经典",
        "星空卫视", "CHANNEL[V]", "凤凰卫视中文台", "凤凰卫视资讯台", "凤凰卫视香港台", "凤凰卫视电影台", "求索纪录", "求索科学",
        "求索生活", "求索动物", "纪实人文", "金鹰纪实", "纪实科教", "睛彩青少", "睛彩竞技", "睛彩篮球", "睛彩广场舞", "魅力足球", "五星体育",
        "劲爆体育", "快乐垂钓", "茶频道", "先锋乒羽", "天元围棋", "汽摩", "梨园频道", "文物宝库", "武术世界", "哒啵赛事", "哒啵电竞", "黑莓电影", "黑莓动画", 
        "乐游", "生活时尚", "都市剧场", "欢笑剧场", "游戏风云", "金色学堂", "动漫秀场", "新动漫", "卡酷少儿", "金鹰卡通", "优漫卡通", "哈哈炫动", "嘉佳卡通", 
        "中国交通", "中国天气", "华数4K", "华数星影", "华数动作影院", "华数喜剧影院", "华数家庭影院", "华数经典电影", "华数热播剧场", "华数碟战剧场",
        "华数军旅剧场", "华数城市剧场", "华数武侠剧场", "华数古装剧场", "华数魅力时尚", "华数少儿动画", "华数动画", "iHOT爱喜剧", "iHOT爱科幻", 
        "iHOT爱院线", "iHOT爱悬疑", "iHOT爱历史", "iHOT爱谍战", "iHOT爱旅行", "iHOT爱幼教", "iHOT爱玩具", "iHOT爱体育", "iHOT爱赛车", "iHOT爱浪漫", 
        "iHOT爱奇谈", "iHOT爱科学", "iHOT爱动漫",
   ],
    "4K频道": [
        "CCTV4K", "北京卫视4K", "东方卫视4K", "广东卫视4K", "深圳卫视4K", "湖南卫视4K", "山东卫视4K", "四川卫视4K", "浙江卫视4K", "江苏卫视4K",
        "欢笑剧场4K", "爱上4K", "4K乐享超清", "绚影4K", "4K纪实", "4K少儿", "4K乐享超清", "天翼高清4K", "BesTV4K电影",
        "BesTV4K记录", "BesTV4K动画", "华数4K"
 ]
}
# ===== 映射（别名 -> 标准名） =====
CHANNEL_MAPPING = {
    "CCTV1": ["CCTV-1", "CCTV-1 HD", "CCTV1 HD", "CCTV-1综合"],
    "CCTV2": ["CCTV-2", "CCTV-2 HD", "CCTV2 HD", "CCTV-2财经"],
    "CCTV3": ["CCTV-3", "CCTV-3 HD", "CCTV3 HD", "CCTV-3综艺"],
    "CCTV4": ["CCTV-4", "CCTV-4 HD", "CCTV4 HD", "CCTV-4中文国际"],
    "CCTV4欧洲": ["CCTV-4欧洲", "CCTV-4欧洲", "CCTV4欧洲 HD", "CCTV-4 欧洲", "CCTV-4中文国际欧洲", "CCTV4中文欧洲"],
    "CCTV4美洲": ["CCTV-4美洲", "CCTV-4北美", "CCTV4美洲 HD", "CCTV-4 美洲", "CCTV-4中文国际美洲", "CCTV4中文美洲"],
    "CCTV5": ["CCTV-5", "CCTV-5 HD", "CCTV5 HD", "CCTV-5体育"],
    "CCTV5+": ["CCTV-5+", "CCTV-5+ HD", "CCTV5+ HD", "CCTV-5+体育赛事"],
    "CCTV6": ["CCTV-6", "CCTV-6 HD", "CCTV6 HD", "CCTV-6电影"],
    "CCTV7": ["CCTV-7", "CCTV-7 HD", "CCTV7 HD", "CCTV-7国防军事"],
    "CCTV8": ["CCTV-8", "CCTV-8 HD", "CCTV8 HD", "CCTV-8电视剧"],
    "CCTV9": ["CCTV-9", "CCTV-9 HD", "CCTV9 HD", "CCTV-9纪录"],
    "CCTV10": ["CCTV-10", "CCTV-10 HD", "CCTV10 HD", "CCTV-10科教"],
    "CCTV11": ["CCTV-11", "CCTV-11 HD", "CCTV11 HD", "CCTV-11戏曲"],
    "CCTV12": ["CCTV-12", "CCTV-12 HD", "CCTV12 HD", "CCTV-12社会与法"],
    "CCTV13": ["CCTV-13", "CCTV-13 HD", "CCTV13 HD", "CCTV-13新闻"],
    "CCTV14": ["CCTV-14", "CCTV-14 HD", "CCTV14 HD", "CCTV-14少儿"],
    "CCTV15": ["CCTV-15", "CCTV-15 HD", "CCTV15 HD", "CCTV-15音乐"],
    "CCTV16": ["CCTV-16", "CCTV-16 HD", "CCTV-16 4K", "CCTV-16奥林匹克", "CCTV16 4K", "CCTV-16奥林匹克4K"],
    "CCTV17": ["CCTV-17", "CCTV-17 HD", "CCTV17 HD", "CCTV-17农业农村"],
    "CCTV4K": ["CCTV4K超高清", "CCTV-4K超高清", "CCTV-4K 超高清", "CCTV 4K"],
    "CCTV8K": ["CCTV8K超高清", "CCTV-8K超高清", "CCTV-8K 超高清", "CCTV 8K"],
    "兵器科技": ["CCTV-兵器科技", "CCTV兵器科技"],
    "风云音乐": ["CCTV-风云音乐", "CCTV风云音乐"],
    "第一剧场": ["CCTV-第一剧场", "CCTV第一剧场"],
    "风云足球": ["CCTV-风云足球", "CCTV风云足球"],
    "风云剧场": ["CCTV-风云剧场", "CCTV风云剧场"],
    "怀旧剧场": ["CCTV-怀旧剧场", "CCTV怀旧剧场"],
    "女性时尚": ["CCTV-女性时尚", "CCTV女性时尚"],
    "世界地理": ["CCTV-世界地理", "CCTV世界地理"],
    "央视台球": ["CCTV-央视台球", "CCTV央视台球"],
    "高尔夫网球": ["CCTV-高尔夫网球", "CCTV高尔夫网球", "CCTV央视高网", "CCTV-高尔夫·网球", "央视高网"],
    "央视文化精品": ["CCTV-央视文化精品", "CCTV央视文化精品", "CCTV文化精品", "CCTV-文化精品", "文化精品"],
    "卫生健康": ["CCTV-卫生健康", "CCTV卫生健康"],
    "电视指南": ["CCTV-电视指南", "CCTV电视指南"],
    "农林卫视": ["陕西农林卫视"],
    "三沙卫视": ["海南三沙卫视"],
    "兵团卫视": ["新疆兵团卫视"],
    "延边卫视": ["吉林延边卫视"],
    "安多卫视": ["青海安多卫视"],
    "康巴卫视": ["四川康巴卫视"],
    "山东教育卫视": ["山东教育", "山东教育卫视 576"],
    "中国教育1台": ["CETV1", "中国教育一台", "中国教育1", "CETV-1 综合教育", "CETV-1"],
    "中国教育2台": ["CETV2", "中国教育二台", "中国教育2", "CETV-2 空中课堂", "CETV-2"],
    "中国教育3台": ["CETV3", "中国教育三台", "中国教育3", "CETV-3 教育服务", "CETV-3"],
    "中国教育4台": ["CETV4", "中国教育四台", "中国教育4", "CETV-4 职业教育", "CETV-4"],
    "早期教育": ["中国教育5台", "中国教育5", "中国教育五台", "CETV早期教育", "华电早期教育", "CETV 早期教育", "CETV-5", "CETV5"],
    "湖南卫视": ["湖南卫视4K"],
    "北京卫视": ["北京卫视4K"],
    "东方卫视": ["东方卫视4K"],
    "广东卫视": ["广东卫视4K"],
    "深圳卫视": ["深圳卫视4K"],
    "山东卫视": ["山东卫视4K"],
    "四川卫视": ["四川卫视4K"],
    "浙江卫视": ["浙江卫视4K"],
    "CHC影迷电影": ["CHC高清电影", "CHC-影迷电影", "影迷电影", "chc高清电影"],
    "淘电影": ["IPTV淘电影", "北京IPTV淘电影", "北京淘电影"],
    "淘精彩": ["IPTV淘精彩", "北京IPTV淘精彩", "北京淘精彩"],
    "淘剧场": ["IPTV淘剧场", "北京IPTV淘剧场", "北京淘剧场"],
    "淘4K": ["IPTV淘4K", "北京IPTV4K超清", "北京淘4K", "淘4K", "淘 4K"],
    "淘娱乐": ["IPTV淘娱乐", "北京IPTV淘娱乐", "北京淘娱乐"],
    "淘BABY": ["IPTV淘BABY", "北京IPTV淘BABY", "北京淘BABY", "IPTV淘baby", "北京IPTV淘baby", "北京淘baby"],
    "淘萌宠": ["IPTV淘萌宠", "北京IPTV萌宠TV", "北京淘萌宠"],
    "魅力足球": ["上海魅力足球"],
    "睛彩青少": ["睛彩羽毛球"],
    "求索纪录": ["求索记录", "求索纪录4K", "求索记录4K", "求索纪录 4K", "求索记录 4K"],
    "金鹰纪实": ["湖南金鹰纪实", "金鹰记实"],
    "纪实科教": ["北京纪实科教", "BRTV纪实科教", "纪实科教8K"],
    "星空卫视": ["星空衛視", "星空衛视", "星空卫視"],
    "CHANNEL[V]": ["CHANNEL-V", "Channel[V]"],
    "凤凰卫视中文台": ["凤凰中文", "凤凰中文台", "凤凰卫视中文", "凤凰卫视"],
    "凤凰卫视香港台": ["凤凰香港台", "凤凰卫视香港", "凤凰香港"],
    "凤凰卫视资讯台": ["凤凰资讯", "凤凰资讯台", "凤凰咨询", "凤凰咨询台", "凤凰卫视咨询台", "凤凰卫视资讯", "凤凰卫视咨询"],
    "凤凰卫视电影台": ["凤凰电影", "凤凰电影台", "凤凰卫视电影", "鳳凰衛視電影台", " 凤凰电影"],
    "茶频道": ["湖南茶频道"],
    "快乐垂钓": ["湖南快乐垂钓"],
    "先锋乒羽": ["湖南先锋乒羽"],
    "天元围棋": ["天元围棋频道"],
    "汽摩": ["重庆汽摩", "汽摩频道", "重庆汽摩频道"],
    "梨园频道": ["河南梨园频道", "梨园", "河南梨园"],
    "文物宝库": ["河南文物宝库"],
    "武术世界": ["河南武术世界"],
    "乐游": ["乐游频道", "上海乐游频道", "乐游纪实", "SiTV乐游频道", "SiTV 乐游频道"],
    "欢笑剧场": ["上海欢笑剧场4K", "欢笑剧场 4K", "欢笑剧场4K", "上海欢笑剧场"],
    "生活时尚": ["生活时尚4K", "SiTV生活时尚", "上海生活时尚"],
    "都市剧场": ["都市剧场4K", "SiTV都市剧场", "上海都市剧场"],
    "游戏风云": ["游戏风云4K", "SiTV游戏风云", "上海游戏风云"],
    "金色学堂": ["金色学堂4K", "SiTV金色学堂", "上海金色学堂"],
    "动漫秀场": ["动漫秀场4K", "SiTV动漫秀场", "上海动漫秀场"],
    "卡酷少儿": ["北京KAKU少儿", "BRTV卡酷少儿", "北京卡酷少儿", "卡酷动画"],
    "哈哈炫动": ["炫动卡通", "上海哈哈炫动"],
    "优漫卡通": ["江苏优漫卡通", "优漫漫画"],
    "金鹰卡通": ["湖南金鹰卡通"],
    "中国交通": ["中国交通频道"],
    "中国天气": ["中国天气频道"],
    "华数4K": ["华数低于4K", "华数4K电影", "华数爱上4K"],
    "iHOT爱喜剧": ["iHOT 爱喜剧", "IHOT 爱喜剧", "IHOT爱喜剧", "ihot爱喜剧", "爱喜剧", "ihot 爱喜剧"],
    "iHOT爱科幻": ["iHOT 爱科幻", "IHOT 爱科幻", "IHOT爱科幻", "ihot爱科幻", "爱科幻", "ihot 爱科幻"],
    "iHOT爱院线": ["iHOT 爱院线", "IHOT 爱院线", "IHOT爱院线", "ihot爱院线", "ihot 爱院线", "爱院线"],
    "iHOT爱悬疑": ["iHOT 爱悬疑", "IHOT 爱悬疑", "IHOT爱悬疑", "ihot爱悬疑", "ihot 爱悬疑", "爱悬疑"],
    "iHOT爱历史": ["iHOT 爱历史", "IHOT 爱历史", "IHOT爱历史", "ihot爱历史", "ihot 爱历史", "爱历史"],
    "iHOT爱谍战": ["iHOT 爱谍战", "IHOT 爱谍战", "IHOT爱谍战", "ihot爱谍战", "ihot 爱谍战", "爱谍战"],
    "iHOT爱旅行": ["iHOT 爱旅行", "IHOT 爱旅行", "IHOT爱旅行", "ihot爱旅行", "ihot 爱旅行", "爱旅行"],
    "iHOT爱幼教": ["iHOT 爱幼教", "IHOT 爱幼教", "IHOT爱幼教", "ihot爱幼教", "ihot 爱幼教", "爱幼教"],
    "iHOT爱玩具": ["iHOT 爱玩具", "IHOT 爱玩具", "IHOT爱玩具", "ihot爱玩具", "ihot 爱玩具", "爱玩具"],
    "iHOT爱体育": ["iHOT 爱体育", "IHOT 爱体育", "IHOT爱体育", "ihot爱体育", "ihot 爱体育", "爱体育"],
    "iHOT爱赛车": ["iHOT 爱赛车", "IHOT 爱赛车", "IHOT爱赛车", "ihot爱赛车", "ihot 爱赛车", "爱赛车"],
    "iHOT爱浪漫": ["iHOT 爱浪漫", "IHOT 爱浪漫", "IHOT爱浪漫", "ihot爱浪漫", "ihot 爱浪漫", "爱浪漫"],
    "iHOT爱奇谈": ["iHOT 爱奇谈", "IHOT 爱奇谈", "IHOT爱奇谈", "ihot爱奇谈", "ihot 爱奇谈", "爱奇谈"],
    "iHOT爱科学": ["iHOT 爱科学", "IHOT 爱科学", "IHOT爱科学", "ihot爱科学", "ihot 爱科学", "爱科学"],
    "iHOT爱动漫": ["iHOT 爱动漫", "IHOT 爱动漫", "IHOT爱动漫", "ihot爱动漫", "ihot 爱动漫", "爱动漫"],
}

# ===============================
# 倒置映射：别名 -> 标准名
def create_reverse_mapping():
    reverse_map = {}
    for standard_name, aliases in CHANNEL_MAPPING.items():
        for alias in aliases:
            reverse_map[alias] = standard_name
    return reverse_map

REVERSE_MAPPING = create_reverse_mapping()

# ===============================
# 确保必要目录存在
def ensure_directories():
    os.makedirs(IP_DIR, exist_ok=True)
    os.makedirs(RTP_DIR, exist_ok=True)

# ===============================
# 计数逻辑
def get_run_count():
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                return int(content) if content.isdigit() else 0
        except Exception as e:
            print(f"⚠️ 读取计数文件失败: {e}")
            return 0
    return 0

def save_run_count(count):
    try:
        with open(COUNTER_FILE, 'w', encoding='utf-8') as f:
            f.write(str(count))
        print(f"📝 保存运行计数: {count}")
    except Exception as e:
        print(f"❌ 保存计数文件失败: {e}")

def check_and_clear_files_by_run_count():
    ensure_directories()
    count = get_run_count() + 1
    if count >= 73:
        print(f"🧹 第 {count} 次运行，清空 {IP_DIR} 下所有 .txt 文件")
        cleared_files = 0
        for f in os.listdir(IP_DIR):
            if f.endswith(".txt"):
                try:
                    os.remove(os.path.join(IP_DIR, f))
                    cleared_files += 1
                except Exception as e:
                    print(f"⚠️ 删除文件 {f} 失败: {e}")
        print(f"🗑️ 已清空 {cleared_files} 个文件")
        save_run_count(1)
        return "w", 1
    else:
        save_run_count(count)
        return "a", count

# ===============================
# IP 运营商判断
def get_isp(ip):
    if ip.startswith(("113.", "116.", "117.", "118.", "119.")):
        return "电信"
    elif ip.startswith(("36.", "39.", "42.", "43.", "58.")):
        return "联通"
    elif ip.startswith(("100.", "101.", "102.", "103.", "104.", "223.")):
        return "移动"
    return "未知"

# ===============================
# 获取省份信息
def get_province_by_ip(ip):
    # 简化版：基于IP前两段判断省份
    ip_parts = ip.split('.')
    if len(ip_parts) < 2:
        return "其他"
    
    ip_prefix = f"{ip_parts[0]}.{ip_parts[1]}"
    
    # IP段到省份的映射（简化版）
    province_map = {
        "113.16": "广东", "113.64": "广东", "113.88": "广东",
        "116.16": "北京", "116.25": "北京", "116.76": "北京",
        "117.22": "天津", "117.80": "江苏",
        "118.26": "河北", "118.74": "山西",
        "119.0": "山西", "119.96": "湖北",
        "36.32": "上海", "36.48": "上海",
        "39.64": "江苏", "39.128": "江苏",
        "42.48": "浙江", "42.224": "浙江",
        "43.224": "安徽", "43.240": "安徽",
        "58.16": "福建", "58.240": "福建",
        "100.64": "移动", "100.128": "移动",
        "101.64": "移动", "101.128": "移动",
        "102.0": "移动", "102.128": "移动",
        "103.0": "移动", "103.128": "移动",
        "104.0": "移动", "104.128": "移动",
        "223.0": "移动", "223.128": "移动",
    }
    
    # 查找最匹配的前缀
    for prefix, province in province_map.items():
        if ip_prefix.startswith(prefix.split('.')[0] + '.'):
            return province
    
    return "其他"

# ===============================
# 标准化频道名称
def normalize_channel_name(ch_name):
    # 如果名称在反向映射中，返回标准名称
    if ch_name in REVERSE_MAPPING:
        return REVERSE_MAPPING[ch_name]
    
    # 检查是否包含标准名称
    for standard_name in CHANNEL_MAPPING.keys():
        if standard_name in ch_name:
            return standard_name
    
    # 检查是否是已知的别名
    for standard_name, aliases in CHANNEL_MAPPING.items():
        for alias in aliases:
            if alias in ch_name:
                return standard_name
    
    # 否则返回原始名称
    return ch_name

# ===============================
# 第一阶段：爬取 + 分类写入
def first_stage():
    print("=" * 50)
    print("📡 第一阶段：爬取FOFA数据并分类")
    print("=" * 50)
    
    all_ips = set()
    for url, filename in FOFA_URLS.items():
        print(f"📡 正在爬取 {filename} ...")
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            
            # 使用正则表达式提取IP地址和端口
            ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+\b'
            urls_all = re.findall(ip_pattern, r.text)
            
            if urls_all:
                print(f"✅ 找到 {len(urls_all)} 个IP")
                all_ips.update(u.strip() for u in urls_all)
            else:
                # 尝试其他模式
                href_pattern = r'href=["\']http://([^"\']+)["\']'
                href_matches = re.findall(href_pattern, r.text)
                for match in href_matches:
                    if ':' in match:
                        all_ips.add(match)
                print(f"✅ 通过href模式找到 {len(href_matches)} 个IP")
                
        except requests.RequestException as e:
            print(f"❌ 爬取失败 {filename}: {e}")
            continue
        except Exception as e:
            print(f"❌ 解析失败 {filename}: {e}")
            continue
        
        time.sleep(2)  # 礼貌延迟

    print(f"🌐 总计爬取到 {len(all_ips)} 个唯一IP")

    province_isp_dict = {}
    ip_processed = 0
    
    for ip_port in all_ips:
        try:
            # 提取IP和端口
            if ':' in ip_port:
                ip = ip_port.split(":")[0]
            else:
                print(f"⚠️ 跳过无效的IP格式: {ip_port}")
                continue
            
            # 获取运营商和省份
            isp = get_isp(ip)
            if isp == "未知":
                # 对于未知运营商，根据常见端口判断
                port = ip_port.split(":")[1] if ':' in ip_port else "80"
                if port in ["8080", "80"]:
                    isp = "通用"
                else:
                    continue
            
            province = get_province_by_ip(ip)
            
            # 创建文件名：省份+运营商
            fname = f"{province}{isp}.txt"
            province_isp_dict.setdefault(fname, set()).add(ip_port)
            ip_processed += 1
            
        except Exception as e:
            print(f"⚠️ 处理IP {ip_port} 失败: {e}")
            continue

    print(f"📊 成功处理 {ip_processed}/{len(all_ips)} 个IP")

    mode, run_count = check_and_clear_files_by_run_count()
    files_written = 0
    
    for filename, ip_set in province_isp_dict.items():
        path = os.path.join(IP_DIR, filename)
        try:
            with open(path, mode, encoding="utf-8") as f:
                for ip_port in sorted(ip_set):
                    f.write(ip_port + "\n")
            files_written += 1
            print(f"📄 {path} 已{'覆盖' if mode=='w' else '追加'}写入 {len(ip_set)} 个 IP")
        except Exception as e:
            print(f"❌ 写入文件 {path} 失败: {e}")

    print(f"✅ 第一阶段完成，当前轮次：{run_count}，写入 {files_written} 个文件")
    return run_count

# ===============================
# 第二阶段：生成 zubo.txt
def second_stage():
    print("=" * 50)
    print("🔔 第二阶段：生成 zubo.txt")
    print("=" * 50)
    
    ensure_directories()
    combined_lines = []
    
    # 检查IP目录
    if not os.path.exists(IP_DIR):
        print("⚠️ IP目录不存在，跳过第二阶段")
        return
    
    ip_files = [f for f in os.listdir(IP_DIR) if f.endswith(".txt")]
    if not ip_files:
        print("⚠️ IP目录中没有txt文件，跳过第二阶段")
        return
    
    for ip_file in ip_files:
        ip_path = os.path.join(IP_DIR, ip_file)
        rtp_path = os.path.join(RTP_DIR, ip_file)
        
        if not os.path.exists(rtp_path):
            print(f"⚠️ RTP文件不存在: {rtp_path}")
            continue

        try:
            with open(ip_path, encoding="utf-8") as f1, open(rtp_path, encoding="utf-8") as f2:
                ip_lines = [x.strip() for x in f1 if x.strip()]
                rtp_lines = [x.strip() for x in f2 if x.strip()]

            if not ip_lines or not rtp_lines:
                continue

            for ip_port in ip_lines:
                for rtp_line in rtp_lines:
                    if "," not in rtp_line:
                        continue
                    
                    ch_name, rtp_url = rtp_line.split(",", 1)
                    
                    # 提取RTP URL部分
                    if "rtp://" in rtp_url:
                        rtp_part = rtp_url.split("rtp://")[1]
                        # 标准化频道名称
                        normalized_name = normalize_channel_name(ch_name)
                        combined_lines.append(f"{normalized_name},http://{ip_port}/rtp/{rtp_part}")
        except Exception as e:
            print(f"❌ 处理文件 {ip_file} 失败: {e}")
            continue

    # 去重：基于URL去重
    unique = {}
    for line in combined_lines:
        try:
            url_part = line.split(",", 1)[1]
            if url_part not in unique:
                unique[url_part] = line
        except:
            continue

    if unique:
        try:
            with open(ZUBO_FILE, "w", encoding="utf-8") as f:
                for line in unique.values():
                    f.write(line + "\n")
            print(f"🎯 第二阶段完成，共 {len(unique)} 条有效 URL")
        except Exception as e:
            print(f"❌ 写入 zubo.txt 失败: {e}")
    else:
        print("⚠️ 没有生成任何有效的URL")

# ===============================
# 第三阶段：检测代表频道并生成 IPTV.txt
def third_stage():
    print("=" * 50)
    print("🧩 第三阶段：检测代表频道生成 IPTV.txt")
    print("=" * 50)
    
    if not os.path.exists(ZUBO_FILE):
        print("⚠️ zubo.txt 不存在，跳过")
        return

    def check_stream(url, timeout=3):
        """检查流是否有效"""
        try:
            # 使用requests检查URL是否可达
            response = requests.head(url, timeout=timeout, headers=HEADERS, allow_redirects=True)
            return response.status_code < 400
        except:
            return False

    # 读取zubo.txt
    groups = {}
    valid_lines = []
    
    try:
        with open(ZUBO_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "," not in line:
                    continue
                
                ch_name, url = line.split(",", 1)
                
                # 提取IP部分用于分组
                ip_match = re.search(r'http://([^/]+)/', url)
                if ip_match:
                    ip = ip_match.group(1)
                    groups.setdefault(ip, []).append((ch_name, url))
                else:
                    # 如果没有匹配到IP，使用URL本身作为分组键
                    groups.setdefault(url, []).append((ch_name, url))
                    
    except Exception as e:
        print(f"❌ 读取 zubo.txt 失败: {e}")
        return

    print(f"📊 从 zubo.txt 读取到 {len(groups)} 个IP组")

    # 检测代表频道（CCTV1）
    total_checked = 0
    max_to_check = min(20, len(groups))  # 限制检查数量
    
    for ip, entries in list(groups.items())[:max_to_check]:
        # 查找代表频道（CCTV1或类似）
        rep_channels = []
        for c, u in entries:
            if "CCTV1" in c or "CCTV-1" in c or c == "CCTV1":
                rep_channels.append(u)
        
        if rep_channels:
            # 检查第一个代表频道
            if check_stream(rep_channels[0]):
                valid_lines.extend(entries)
                total_checked += 1
        else:
            # 如果没有CCTV1，检查任意频道
            if entries and check_stream(entries[0][1]):
                valid_lines.extend(entries)
                total_checked += 1

    print(f"📡 检测到 {len(valid_lines)} 条有效频道，检查了 {total_checked} 个IP组")

    # 分类 + 严格排序 + URL 去重
    try:
        with open(IPTV_FILE, "w", encoding="utf-8") as f:
            for cat, channel_order in CHANNEL_CATEGORIES.items():
                f.write(f"{cat},#genre#\n")
                cat_added = 0
                
                for standard_ch in channel_order:
                    seen_urls = set()
                    
                    # 收集所有匹配的频道
                    matched_entries = []
                    for c, url in valid_lines:
                        # 标准化频道名称
                        normalized = normalize_channel_name(c)
                        
                        # 检查是否匹配标准频道或别名
                        if (standard_ch == normalized or 
                            standard_ch in normalized or 
                            normalized in standard_ch or
                            (standard_ch in REVERSE_MAPPING and REVERSE_MAPPING.get(c, "") == standard_ch)):
                            matched_entries.append((c, url))
                    
                    # 去重并写入
                    for c, url in matched_entries:
                        if url not in seen_urls:
                            f.write(f"{c},{url}\n")
                            seen_urls.add(url)
                            cat_added += 1
                
                if cat_added > 0:
                    f.write("\n")
                    
        print(f"✅ IPTV.txt 生成完成，共 {len(valid_lines)} 条原始数据")
        
    except Exception as e:
        print(f"❌ 写入 IPTV.txt 失败: {e}")

# ===============================
# 主执行逻辑
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 开始执行 FOFA IPTV 数据抓取脚本")
    print("=" * 60)
    
    try:
        # 创建必要目录
        ensure_directories()
        
        # 第一阶段：爬取数据
        run_count = first_stage()
        
        # 根据运行计数决定是否执行第二、三阶段
        # 原逻辑：每12次运行执行一次，但为了GitHub Actions稳定，我们调整逻辑
        # 在GitHub Actions中，我们可以让每次运行都生成完整文件
        should_execute = run_count in [12, 24, 36, 48, 60, 72] or run_count <= 3
        
        if should_execute:
            print(f"🔧 执行第二、三阶段 (运行计数: {run_count})")
            second_stage()
            third_stage()
        else:
            print(f"⏭️  跳过第二、三阶段 (运行计数: {run_count})")
        
        print("=" * 60)
        print("✅ 脚本执行完成")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断执行")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 脚本执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
