import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.database import SessionLocal
from app.models.knowledge import Knowledge

SEEDS = [
    {"title":"物流查询","question":"我的快递到哪了？","answer":"请提供您的订单号，我帮您查询物流进度。您也可以在「我的订单」页面查看实时物流轨迹。","category":"物流","tags":"快递,物流,配送"},
    {"title":"退换货政策","question":"商品不满意怎么退换货？","answer":"我们支持7天无理由退换货。请在订单详情页申请退货/换货，审核通过后按指引寄回商品即可。退回商品需保持完好，不影响二次销售。","category":"售后","tags":"退货,换货,退款"},
    {"title":"发货时间","question":"下单后多久能发货？","answer":"一般订单在付款后24小时内发货，定制商品需3-5个工作日。您可在订单详情页查看预计发货时间，我们会尽快为您安排。","category":"物流","tags":"发货,时效"},
    {"title":"优惠券使用","question":"优惠券怎么用？","answer":"下单时在结算页面选择可用优惠券即可抵扣。注意查看优惠券的使用条件和有效期，部分商品可能不参与优惠。","category":"促销","tags":"优惠券,折扣,促销"},
    {"title":"支付方式","question":"支持哪些支付方式？","answer":"支持微信支付、支付宝、银行卡和花呗分期付款。大额订单可选择分期，手续费详见支付页面说明。","category":"支付","tags":"支付,微信,支付宝"},
    {"title":"订单取消","question":"怎么取消订单？","answer":"未发货订单可直接在订单详情页取消，款项将在1-3个工作日原路退回。已发货订单需先申请退款/退货。","category":"订单","tags":"取消,订单"},
    {"title":"商品对比咨询","question":"iPhone 15 Pro和华为Mate 60 Pro拍照哪个好？","answer":"两款都是旗舰影像手机。iPhone 15 Pro色彩真实自然、视频拍摄能力强；Mate 60 Pro变焦和暗光表现突出，人像模式优秀。具体可以查看商品详情页的实拍样张对比，根据您的使用偏好选择。","category":"商品咨询","tags":"对比,拍照,手机"},
    {"title":"会员权益","question":"会员有什么权益？","answer":"会员享受全场9折优惠、生日专属礼包、专属客服通道和免费退货特权。开通后在「我的-会员中心」查看全部权益。","category":"账户","tags":"会员,权益,折扣"},
    {"title":"发票开具","question":"怎么开发票？","answer":"下单时可勾选开具电子发票或纸质发票。已完成订单也可在订单详情页补开，电子发票即时发送到您的邮箱。","category":"支付","tags":"发票,报销"},
    {"title":"投诉建议","question":"我要投诉！","answer":"非常抱歉给您带来不好的体验。已为您记录反馈，人工客服将尽快与您联系处理。您也可以拨打400客服热线直接沟通。","category":"售后","tags":"投诉,建议"},
]

def seed():
    db = SessionLocal()
    existing = db.query(Knowledge).count()
    if existing > 0:
        print(f'已有 {existing} 条知识，跳过种子数据')
        db.close()
        return

    for item in SEEDS:
        k = Knowledge(**item, keywords=item['tags'], status='published')
        db.add(k)
    db.commit()
    print(f'已导入 {len(SEEDS)} 条种子知识')
    db.close()

if __name__ == '__main__':
    seed()
