# 关于页头像补边

2026-10-23，使用内置 image_gen 图片编辑工具。目标为补齐原图四周浅灰留白，延展蓝黄网点画面，适应网页圆形裁切。

- 输入原图：`docs/assets/profile/avatar.jpg`（保留备份）。
- 当前使用：`docs/assets/profile/avatar-filled.png`。
- 网页边框调整为细线，避免额外的浅色厚边。

实际使用的提示词：

```text
Use case: precise-object-edit. Edit target: the attached square 1200 x 1200 avatar image. Task: remove ONLY the light grey/off-white rectangular mat/border occupying about the outermost 90 pixels on all four sides, and inpaint/extend the existing illustration seamlessly through those border areas all the way to the square canvas edges. Preserve the current central artwork, face, eyes, hand pose, character identity, framing, scale, and relative position as faithfully as possible; do not zoom or crop. Continue the dark cobalt blue hair/background, pale yellow skin, blue/yellow halftone dots and geometric dot textures naturally at the outer edges, using the immediate neighboring content to determine each edge's color and pattern. Preserve the small red lower-left region where appropriate. The final image must be a fully opaque edge-to-edge square pop-art illustration, with absolutely no white/grey mat, blank strips, rounded frame, border, transparency, added text or watermark. This will be clipped into a circle on a website, so the circular perimeter must show continuous illustration rather than pale blank arcs.
```
