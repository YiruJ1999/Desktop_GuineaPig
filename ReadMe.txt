🐹 DesktopPet 桌面宠物

A cute animated desktop pet built with Python (PySide6)!
可爱的桌面宠物程序，用 Python (PySide6) 编写！

------------------------------------
🌟 Features / 功能介绍

🖥️ On the Desktop / 桌面功能
- Walking animation — The pet walks around your desktop.
  行走动画 — 宠物会在桌面上四处走动。
- Sleeping animation — When idle, the pet goes to sleep.
  睡觉动画 — 宠物在空闲时会进入睡眠状态。

------------------------------------
🎮 Interactions / 交互功能

1. 💩 Random Pooping
   - The pet may randomly poop while walking!
   - A “Pick Up Poop” button allows the user to clean it up.
   宠物会在行走时随机拉便便！
   用户可以点击按钮清理💩。

2. 🖱️ Dragging and Falling
   - You can drag the pet anywhere on your desktop.
   - When released, it will fall back to the ground realistically.
   你可以拖动宠物到桌面的任意位置，松手后它会自然下落回地面。

------------------------------------
🧩 Project Structure / 项目结构

DesktopPet/
│
├── main.py                # Entry point / 程序入口
├── MainWindow.py          # Main application window / 主窗口
├── DesktopPet.py          # Core pet logic & animations / 宠物动画逻辑
├── PetHouse.py            # The pet’s house / 宠物小屋
├── Carpet.py              # Ground background / 地毯背景
├── PoopWidget.py          # Poop display / 💩控件
└── frames/                # Animation frames / 动画帧图像

------------------------------------
🚀 How to Run / 运行方式

Requirements / 依赖
- Python 3.9+
- PySide6
- NumPy

Install dependencies:
pip install PySide6 numpy

Run / 启动:
python main.py

------------------------------------
💡 Tips / 使用提示
- Try dragging the pet around to see it fall!
- Watch out — it might poop at any time 😆
- Click the ❌ button on the window to close the app.

拖动宠物看看它如何下落！
小心，它随时可能拉💩～
点击右上角 ❌ 关闭程序。

------------------------------------
🧑‍💻 Author / 作者
DesktopPet Project — Made with ❤️ using Python & PySide6 — YiruJ
用爱制作的桌面宠物项目 — YiruJ
