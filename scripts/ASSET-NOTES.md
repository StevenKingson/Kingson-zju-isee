# 角色素材说明

本次使用内置 image_gen 工具。原始画集保持不变，生成的透明 PNG 放在 `docs/assets/characters/`。

| 文件 | 参照 | 用途 |
| --- | --- | --- |
| theme-day.png | 210 号底部从左数第二位，举起双手的平泽唯 | 白天主题按钮 |
| theme-night.png | 182 号左侧的平泽唯；210 号的 Q 版比例；242 号左侧的奶油黄条纹睡衣 | 夜晚主题按钮，含配套长裤和左眼哈欠泪珠 |
| pet-150.png … pet-158.png | 对应 150–158 号人物及桌椅 | 课程页陪读角色 |

播放器的五个人物头像直接通过 CSS 从 119、120 号原图定位显示，没有改动画集源文件。

## 白天图标提示词

Create a transparent-background UI character cutout. Reference image 210.jpg: extract and faithfully redraw ONLY the chibi girl who is SECOND FROM THE LEFT IN THE BOTTOM ROW (short light brown bob hair, Yui, both arms raised, happy closed eyes, light blue T shirt with small donut graphic, dark blue pants and burgundy boots, one knee lifted). Preserve her original cute chibi proportions, cheerful expression, full body, clothing and pose. No striped pink background, no other characters, no cake, no stars, no text, no logo. Single isolated character centered with small even padding, genuine alpha, crisp high quality anime linework. Square canvas.

## 夜晚图标提示词

Generate one full-body CHIBI character PNG on transparent background for a night theme switch icon. Identity reference: the girl on the LEFT in image 182.jpg, Yui with a short chestnut brown bob and two gold hair clips on the side, eyes gently CLOSED with a sleepy yawning open mouth, one arm stretched upward, other hand beside cheek, light blue short-sleeved school shirt with blue bow, dark pleated skirt, dark socks. Style reference: image 210.jpg bottom row second girl from left, match that same large cute head, tiny body, rounded anime chibi proportions and crisp linework. Reinterpret the sleepy pose upright and standing, no other people, no pillow/background, no logo/text, no extra objects. Single isolated full-body centered character, square canvas, evenly padded, true transparency.

## 夜晚图标第二版：242 号睡衣与左眼泪珠

使用内置 image_gen 编辑原夜间图标，242 号仅作为服装参考。旧版保存在 `output/asset-history/theme-night-school.png`，当前使用 `docs/assets/characters/theme-night.png`。角色自身左眼对应画面右侧。

Edit target Image 1 (the existing transparent night-theme chibi Yui icon). Image 2 (242.jpg) is CLOTHING REFERENCE ONLY: use the pajamas worn by the LEFT brown-haired girl, NOT the blonde girl's mint outfit. Preserve Image 1's exact cute chibi identity, short chestnut bob, two gold side hair clips, large head / small body proportions, sleepy closed eyes and yawning open mouth, raised right arm and left hand near cheek, pose, centered full body framing and crisp anime linework. Change ONLY the clothing and add one yawn tear. Replace the school shirt, blue bow, dark skirt, socks and shoes with a cozy full matching pajama set: pale butter-yellow and creamy ivory broad horizontal stripes, long fluffy sleeves, soft hood/collar, mint-green sleeve cuffs, mint drawstrings with small light lavender-pink fluffy pom-poms and mint bunny-silhouette pockets, following the LEFT character's top in 242.jpg. Invent matching loose long pajama trousers in the same cream/yellow striped fabric with mint ankle cuffs, plus simple soft cream house slippers. Keep the pajama costume readable at small icon size. Add ONE clearly visible small glossy pale blue translucent teardrop at the OUTER CORNER OF THE CHARACTER'S OWN LEFT CLOSED EYE (the eye on the VIEWER'S RIGHT), as a yawning tear on the cheek close to that eyelid; do not put it on the opposite eye. No crying expression, preserve yawning expression. Do not add pillows, background, scenery, other people, moons, text, watermark, decorative symbols or floor shadow. Genuine transparent alpha background, square canvas, whole body fully visible with even small padding. Keep existing transparency.

## 九个陪读角色提示词

以下提示词分别使用一次，`{n}` 依次是 150、151、152、153、154、155、156、157、158，每次只提供对应的原图：

Transparent background extraction asset for a website desktop companion. Edit the provided image {n}.jpg. Remove the entire colored polka dot wallpaper, all white dots, top-left K-ON logo and bottom-right copyright text. Retain ONLY the entire original girl with her school desk, chair, schoolbag, book/pencils and all attached accessories, preserving her EXACT face, hairstyle, original drawing, pose, clothing, desk geometry and colors. This is a clean faithful cutout, not a chibi redesign. Center the retained girl and desk ensemble tightly with small padding on a square or portrait transparent canvas. No extra character, no text, no shadows outside the original illustration, genuine alpha transparency. Every desk leg and the full head must be visible.
