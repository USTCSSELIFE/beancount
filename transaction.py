from login import Login
from lxml import etree
from datetime import datetime
import csv
from config import UID, PWD


def get_today_paylist():
    login = Login(UID, PWD)
    session = login.login()

    ECARD_HP = "https://ecard.ustc.edu.cn/paylist"
    ECARD_URL = "https://ecard.ustc.edu.cn/paylist/ajax_get_paylist"

    paylist = session.get(ECARD_HP)
    token = etree.HTML(paylist.text).xpath("//input[@name='_token']/@value")[0]

    headers = {
        "x-csrf-token": token,
    }
    data = {
        "page": "", "date": ""
    }
    resp = session.post(ECARD_URL, headers=headers, data=data)

    return etree.HTML(resp.text)


def get_today_txn_list():
    txns = []

    items = get_today_paylist().xpath("//tr")
    for item in items[1:]:
        line = [td.text for td in item.xpath(".//td")]
        if len(line) == 1 and line[0] == "没有数据":
            break

        today = datetime.now()
        date = datetime.strptime(line[5], "%Y-%m-%d %H:%M:%S")
        if date.day != today.day:
            break

        txn = {
            "类别": "",
            "日期": date,
            "金额": float(line[4]),
            "地点": line[6],
            "机号": line[7]
        }
        if line[0] == "圈存机充值" and line[1] == '0':
            txn["类别"] = "圈存机充值"
            txn["金额"] = -txn["金额"]
        elif line[0] == "主机补助":
            txn["类别"] = "主机补助"
            txn["金额"] = -txn["金额"]
        elif line[0] == "消费":
            txn["类别"] = "消费"
        else:
            continue

        txns.append(txn)

    # 按时间 ASC 排序
    return txns[::-1]


def write_csv():
    txns = get_today_txn_list()
    headers = ["日期", "金额",  "地点", "机号", "类别"]
    with open(datetime.now().strftime("%Y-%m-%d") + ".csv", "w") as f:
        writer = csv.DictWriter(f, headers)
        writer.writeheader()
        writer.writerows(txns)
