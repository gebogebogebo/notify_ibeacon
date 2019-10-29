# notify_ibeacon
ラズパイ、MAMORIO、LINE Notifyとかをつかったサンプル

## notify_ibeacon.py
詳細は[Qiita](https://qiita.com/gebo/items/4fa5a3d0866bce6cfae2)を参照

## notify_ibeacon_sg90.py
notify_ibeacon.pyに追加して、サーボモータを動かす。
- [サーボモータ SG90](https://www.amazon.co.jp/dp/B016FKJJ8M/ref=cm_sw_r_tw_dp_U_x_StbUDbJ57W8GQ) ￥889
- [ジャンパーワイヤ（メス-オス）（20cm）40本](https://www.amazon.co.jp/dp/B00P9BVKOK/ref=cm_sw_r_tw_dp_U_x_gwbUDbPJEYN15) ￥197

### 接続
- SG90.黄色 --> ラズパイ.GPIO.2
- SG90.オレンジ(赤) --> ラズパイ.GPIO.5V
- SG90.茶(黒) --> ラズパイ.GPIO.5V
