import sys,random, csv, os
from PySide6.QtWidgets import (QApplication,QWidget,QLabel,QPushButton,QVBoxLayout,QHBoxLayout,QFrame,QGridLayout,QStackedWidget,QButtonGroup)
from PySide6.QtGui import QFont
from PySide6.QtCore import QRect, QPropertyAnimation, QEasingCurve, Qt,QTimer

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# ================= CARD =================
class FlipCard(QPushButton):
    def __init__(self,parent):
        super().__init__()
        self.parent_ui=parent
        self.value=None
        self.is_open=False
        self.setFixedSize(92,122)
        self.raw_value = None
        self.default_style="""
        QPushButton{
            background:#030a1f;
            border:1px solid #0f172a;
            border-radius:16px;
            color:#64748b;
            font-size:13px;
        }
        QPushButton:hover{
            border:1px solid #3b82f6;
        }
        """
        self.highlight_style="""
        QPushButton{
            background:#030a1f;
            border:1px solid #001335;
            border-radius:16px;
            color:#94a3b8;
        }
        """
        self.face_style = """
        QPushButton{
            background:#0b1229;
            border:2px solid #60a5fa;
            border-radius:16px;
            color:white;
            font-size:10px;
            font-weight:bold;
            padding:6px;
            text-align:center;
        }
        """
        self.setStyleSheet(self.default_style)
        self.setText("TESMEE")
        self.setStyleSheet(self.styleSheet() + "\nQPushButton{ text-align:center; padding:6px; }")
        self.clicked.connect(self.on_click)
        
    def on_click(self):
        self.parent_ui.card_clicked(self)
        
    def open_card(self,value):
        self.value=value
        self.is_open=True
        self.setText(value)
        self.setStyleSheet(self.face_style)
        
    def close_card(self):
        self.value=None
        self.is_open=False
        self.setText("TESMEE")
        self.setStyleSheet(self.highlight_style)
        
    def highlight(self):
        if not self.is_open:
            self.setStyleSheet(self.highlight_style)
            
    def remove_highlight(self):
        if not self.is_open:
            self.setStyleSheet(self.default_style)

            
            
# ================= MAIN UI =================
class ProjectXUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TESMEE")
        self.resize(1000,550)
        self.game_active=False
        self.open_cards=[]
        self.input_locked=False
        app_dir = os.path.join(os.path.expanduser("~"), ".tesmee")
        os.makedirs(app_dir, exist_ok=True)
        self.save_path = os.path.join(app_dir, "rating.txt")
        self.data = []

        try:
            with open(resource_path("data.csv"), newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 6:
                        self.data.append(row)
        except Exception as e:
            print("CSV ERROR:", e)
        self.combination_pool=[]
        self.valid_sets=set()
        self.correct_submits=0
        self.total_submits=0
        self.start_time=None
        self.my_rating=100
        try:
            with open(self.save_path,"r") as f:
                self.my_rating = round(float(f.read().strip()))
        except:
            pass
        self.build_ui()

    def smooth_scroll(self, delta):
        bar = self.scroll.verticalScrollBar()

        anim = QPropertyAnimation(bar, b"value")
        anim.setDuration(200)
        anim.setStartValue(bar.value())
        anim.setEndValue(bar.value() - delta)
        anim.setEasingCurve(QEasingCurve.OutCubic)

        anim.start()
        self.scroll_anim = anim  # prevent garbage collection
        
    # ================= UI ROOT =================
    def build_ui(self):
        root=QHBoxLayout(self)
        root.setContentsMargins(0,0,0,0)
        sidebar=QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet("background:#01040f;")
        s_layout=QVBoxLayout(sidebar)
        s_layout.setContentsMargins(20,30,20,20)
        s_layout.setSpacing(20)
        title=QLabel("TESMEE")
        title.setFont(QFont("Inter",34,QFont.Black))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color:#e2e8f0;")
        s_layout.addWidget(title)
        accent=QFrame()
        accent.setFixedHeight(2)
        accent.setStyleSheet("background:#3b82f6;")
        s_layout.addWidget(accent)
        self.btn_dashboard=QPushButton("Dashboard")
        self.btn_game=QPushButton("Game")
        for b in (self.btn_dashboard,self.btn_game):
            b.setStyleSheet("""
            QPushButton{
                color:#94a3b8;
                padding:16px;
                border-radius:12px;
                text-align:left;
            }
            QPushButton:hover{
                background:#02071a;
                color:#e2e8f0;
            }
            QPushButton[selected="true"]{
                background:#3b82f6;
                color:white;
            }
            """)
        self.btn_dashboard.setProperty("selected",True)
        self.btn_dashboard.clicked.connect(lambda:self.switch_page(0))
        self.btn_game.clicked.connect(lambda:self.switch_page(1))
        s_layout.addWidget(self.btn_dashboard)
        s_layout.addWidget(self.btn_game)
        s_layout.addStretch()
        self.pages=QStackedWidget()
        self.pages.addWidget(self.dashboard_page())
        self.pages.addWidget(self.game_page())
        root.addWidget(sidebar)
        root.addWidget(self.pages)

    def wrap_widget(self, widget):
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(widget)
        layout.addStretch()
        return layout
    
    def toggle_topic_menu(self):
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve

        # ✅ correct positioning (relative to window)
        pos = self.topic_btn.mapTo(self.window(), self.topic_btn.rect().bottomLeft())
        self.topic_menu.move(pos)

        if self.topic_menu.isVisible():
            # CLOSE animation
            self.anim = QPropertyAnimation(self.topic_menu, b"maximumHeight")
            self.anim.setDuration(150)
            self.anim.setStartValue(self.topic_menu.height())
            self.anim.setEndValue(0)
            self.anim.setEasingCurve(QEasingCurve.InCubic)

            def hide_menu():
                self.topic_menu.setVisible(False)

            self.anim.finished.connect(hide_menu)
            self.anim.start()

        else:
            btn_pos = self.topic_btn.mapTo(self.window(), self.topic_btn.rect().bottomLeft())

            start_rect = QRect(btn_pos.x(), btn_pos.y(), self.topic_btn.width(), 0)
            end_rect = QRect(btn_pos.x(), btn_pos.y(), self.topic_btn.width(), 140)

            self.anim = QPropertyAnimation(self.topic_menu, b"geometry")
            self.anim.setDuration(200)
            self.anim.setStartValue(start_rect)
            self.anim.setEndValue(end_rect)
            self.anim.setEasingCurve(QEasingCurve.OutCubic)

            self.topic_menu.setGeometry(start_rect)
            self.topic_menu.show()
            self.topic_menu.raise_()

            self.anim.start()


    def select_topic(self, topic):
        self.topic_btn.setText(f"{topic} ⌄")
        self.selected_topic = topic
        self.topic_menu.setVisible(False)

    # ================= PAGE SWITCH =================
    def switch_page(self,index):
        self.pages.setCurrentIndex(index)
        self.btn_dashboard.setProperty("selected",index==0)
        self.btn_game.setProperty("selected",index==1)
        for b in (self.btn_dashboard,self.btn_game):
            b.style().unpolish(b)
            b.style().polish(b)

    def show_explanation(self, text, color="#93c5fd"):
        if not text:
            return

        self.explanation_label.setStyleSheet(f"""
        QLabel{{
            color:{color};
            font-size:16px;
            padding:10px;
        }}
        """)

        self.explanation_label.setText(text)
        self.explanation_label.setVisible(True)

        QTimer.singleShot(3500, lambda: self.explanation_label.setVisible(False))
            
    # ================= DASHBOARD =================
    def dashboard_page(self):
        from PySide6.QtWidgets import QGraphicsBlurEffect, QScrollArea
        from PySide6.QtGui import QPixmap, QFont
        from PySide6.QtCore import Qt

        page = QFrame()
        page.setStyleSheet("background:#01030a;")

        outer = QVBoxLayout(page)
        outer.addStretch()

        # ================= MAIN BOX =================
        box = QFrame()
        box.setObjectName("mainbox")
        box.setMaximumWidth(900)

        box.setStyleSheet("""
        QFrame#mainbox{
            background:rgba(2,7,26,110);
            border-radius:28px;
            border:1px solid rgba(255,255,255,40);
        }
        """)

        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(60,60,60,60)
        box_layout.setSpacing(36)

        # ================= TITLE =================
        hero = QLabel("TESMEE")
        hero.setFont(QFont("Inter",56,QFont.Black))
        hero.setAlignment(Qt.AlignCenter)
        hero.setStyleSheet("color:white; background:transparent; border:none;")
        box_layout.addWidget(hero)

        # ================= RATING =================
        self.rating_label = QLabel(f"RATING\n{self.my_rating}")
        self.rating_label.setAlignment(Qt.AlignCenter)
        self.rating_label.setFixedSize(260,140)
        self.rating_label.setStyleSheet("""
        QLabel{
            background:rgba(3,10,31,130);
            border:1px solid rgba(255,255,255,35);
            border-radius:24px;
            font-size:28px;
            font-weight:bold;
            color:white;
        }
        """)

        # ================= TOPIC BUTTON =================
        self.topic_btn = QPushButton("Mixed ⌄")
        self.topic_btn.setFixedHeight(48)

        self.topic_btn.setStyleSheet("""
        QPushButton{
            background:#020d1f;
            border-radius:14px;
            color:white;
            font-size:15px;
            padding:10px;
            border:1px solid rgba(255,255,255,40);
        }
        QPushButton:hover{
            background:#051736;
        }
        """)

        self.topic_btn.clicked.connect(self.toggle_topic_menu)

        box_layout.addWidget(self.rating_label, alignment=Qt.AlignCenter)
        box_layout.addWidget(self.divider())

        # ================= CONTROLS =================
        controls = QHBoxLayout()
        controls.setSpacing(40)

        controls.addWidget(
            self.control_card(
                "Difficulty",
                self.exclusive_buttons(["Basic","Advanced","Mixed"], "difficulty")
            )
        )

        controls.addWidget(
            self.control_card(
                "Topics",
                self.wrap_widget(self.topic_btn)
            )
        )

        self.selected_topic = "Mixed"

        box_layout.addLayout(controls)
        box_layout.addWidget(self.divider())

        # ================= PLAY BUTTON =================
        self.play_btn = QPushButton("PLAY")
        self.play_btn.setFixedHeight(90)

        self.play_btn.setStyleSheet("""
        QPushButton{
            background:#020d1f;
            font-size:26px;
            font-weight:bold;
            border-radius:24px;
            color:white;
            border:1px solid rgba(255,255,255,40);
        }
        QPushButton:hover{
            background:#051736;
            border:1px solid rgba(255,255,255,90);
        }
        QPushButton:pressed{
            background:#051736;
        }
        """)

        self.play_btn.clicked.connect(self.start_game)
        box_layout.addWidget(self.play_btn)

        outer.addWidget(box, alignment=Qt.AlignHCenter)
        outer.addStretch()

        # ================= DROPDOWN MENU =================
        self.topic_menu = QFrame(self.window())
        self.topic_menu.setVisible(False)

        self.topic_menu.setStyleSheet("""
        QFrame{
            background:#01030a;   /* same as screen */
            border-radius:14px;
            border:1px solid rgba(255,255,255,25);
        }
        """)

        scroll = QScrollArea(self.topic_menu)
        self.scroll = scroll

        def wheelEvent(event):
            self.smooth_scroll(event.angleDelta().y() / 4)

        scroll.wheelEvent = wheelEvent
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll.setStyleSheet("""
        QScrollArea{
            border:none;
            background:transparent;
        }
        QScrollArea > QWidget > QWidget{
            background:#01030a;
        }
        QScrollBar:vertical{
            background:#020d1f;
            width:6px;
            margin:4px;
        }
        QScrollBar::handle:vertical{
            background:#3b82f6;
            border-radius:3px;
        }
        """)

        container = QWidget()
        container.setStyleSheet("background:#01030a;")
        menu_layout = QVBoxLayout(container)
        menu_layout.setContentsMargins(10,10,10,10)
        menu_layout.setSpacing(6)

        self.topic_options = [
            "Mixed","Mathematics","Science","Arts",
            "Sports","Commerce","Dates","Nations"
        ]

        for t in self.topic_options:
            b = QPushButton(t)
            b.setMinimumHeight(40)
            b.setCursor(Qt.PointingHandCursor)

            b.setStyleSheet("""
            QPushButton{
                background:rgba(2,13,31,180);
                padding:10px;
                border-radius:10px;
                color:#cbd5f5;
                text-align:left;
                border:1px solid rgba(255,255,255,20);
            }
            QPushButton:hover{
                background:#3b82f6;
                color:white;
                border:1px solid rgba(255,255,255,60);
            }
            """)

            b.clicked.connect(lambda _, x=t: self.select_topic(x))
            menu_layout.addWidget(b)

        menu_layout.addStretch()

        scroll.setWidget(container)

        dropdown_layout = QVBoxLayout(self.topic_menu)
        dropdown_layout.setContentsMargins(0,0,0,0)
        dropdown_layout.addWidget(scroll)

        scroll.verticalScrollBar().setSingleStep(5)
        scroll.verticalScrollBar().setPageStep(40)

        # size control
        self.topic_menu.setFixedWidth(150)
        self.topic_menu.setFixedHeight(110)

        return page
    # ================= GAME =================
    def game_page(self):
        page=QWidget()
        page.setStyleSheet("background:#020513;")
        layout=QVBoxLayout(page)
        layout.setContentsMargins(40,40,40,40)
        layout.setSpacing(24)
        self.cards=[]
        grid=QGridLayout()
        grid.setSpacing(20)
        for r in range(5):
            for c in range(6):
                card=FlipCard(self)
                self.cards.append(card)
                grid.addWidget(card,r,c)
        layout.addWidget(self.panel(grid,"#02071a"))
        btn_row=QHBoxLayout()
        btn_row.setSpacing(32)
        self.submit_btn=QPushButton("Submit")
        quit_btn=QPushButton("Quit Game")
        for b,col in [(self.submit_btn,"#3b82f6"),(quit_btn,"#1e293b")]:
            b.setFixedSize(200,52)
            b.setStyleSheet(f"""
            QPushButton{{
                background:{col};
                border-radius:16px;
                font-size:18px;
                font-weight:bold;
                color:white;
            }}
            QPushButton:hover{{
                background:#60a5fa;
            }}
            """)
        self.submit_btn.setDisabled(True)
        self.submit_btn.clicked.connect(self.submit_cards)
        quit_btn.clicked.connect(self.end_game)
        btn_row.addStretch()
        btn_row.addWidget(self.submit_btn)
        btn_row.addWidget(quit_btn)
        btn_row.addStretch()

        self.explanation_label = QLabel("")
        self.explanation_label.setAlignment(Qt.AlignCenter)
        self.explanation_label.setStyleSheet("""
        QLabel{
            color:#93c5fd;
            font-size:16px;
            padding:10px;
        }
        """)
        self.explanation_label.setVisible(False)

        layout.addWidget(self.explanation_label)

        layout.addLayout(btn_row)
        return page
    # ================= GAME LOGIC =================
    def get_selected(self, key):
        if key == "topic":
            return getattr(self, "selected_topic", "Mixed")

        group = self.button_groups.get(key)
        if not group:
            return None

        for btn in group.buttons():
            if btn.isChecked():
                return btn.text()

        return None
    
    def start_game(self):
        if self.game_active:
            return
        self.game_active = True
        self.input_locked = False
        self.open_cards.clear()
        self.combination_pool.clear()

        self.correct_submits = 0
        self.total_submits = 0

        difficulty = self.get_selected("difficulty")
        topic = self.get_selected("topic")

        valid_combinations = []

        # 🔹 FILTER CSV PROPERLY
        for row in self.data:
            clue1, clue2, clue3, difficulty_csv, topic_csv, explanation = [x.strip() for x in row]

            if difficulty and difficulty != "Mixed":
                if difficulty.lower() != difficulty_csv.lower():
                    continue

            if topic and topic != "Mixed":
                if topic.lower() != topic_csv.strip().lower():
                    continue

            valid_combinations.append([clue1, clue2, clue3, explanation])

        if len(valid_combinations) < 10:
            print("NOT ENOUGH COMBINATIONS")
            self.game_active = False
            return
        
        # 🔹 PICK 10 RANDOM COMBINATIONS
        random.shuffle(valid_combinations)
        selected = valid_combinations[:10]

        self.valid_sets = set()
        self.explanations = {}

        for combo in selected:
            clues = combo[:3]
            explanation = combo[3]

            key = frozenset(clues)
            self.valid_sets.add(key)
            self.explanations[key] = explanation

        # 🔹 FLATTEN → 30 VALUES
        pool = []
        for combo in selected:
            pool.extend(combo[:3])

        # 🔹 SHUFFLE FINAL CARD VALUES
        random.shuffle(pool)
        self.combination_pool = pool

        # 🔹 ASSIGN VALUES TO CARDS (IMPORTANT)
        for i, card in enumerate(self.cards):
            card.setDisabled(False)   # safety reset
            value = self.combination_pool[i]

            card.raw_value = value   # permanent value

            card.close_card()
            card.highlight()

        self.submit_btn.setDisabled(True)

        import time
        self.start_time=time.time()

        self.switch_page(1)

        print("Selected combinations:", selected)
        print("Pool size:", len(self.combination_pool))
    
    def end_game(self):
        if self.game_active:   # only penalize if quitting mid-game
            self.my_rating = max(0, self.my_rating - 5)
            self.update_rating(self.my_rating)

            try:
                with open(self.save_path,"w") as f:
                    f.write(str(self.my_rating))
            except:
                pass

        self.game_active=False
        self.play_btn.setDisabled(False)
        self.open_cards.clear()

        for c in self.cards:
            c.setDisabled(False)   # 🔥 THIS IS THE FIX
            c.close_card()
            c.remove_highlight()

        self.submit_btn.setDisabled(True)
        self.switch_page(0)

    def card_clicked(self,card):
        if(not self.game_active or self.input_locked or card.is_open):
            return
        
        value = card.raw_value

        words = value.split()
        if len(words) > 1:
            display = "\n".join(words)
        else:
            display = value

        card.open_card(display)

        card.setStyleSheet(card.styleSheet() + "\nQPushButton{ text-align:center; padding:6px; }")
        self.open_cards.append(card)
        self.submit_btn.setDisabled(len(self.open_cards)!=3)
        if len(self.open_cards)==3:
            self.input_locked=True
            QTimer.singleShot(2000,self.safe_close_open_cards)

    def safe_close_open_cards(self):
        if not self.open_cards:
            return

        for c in self.open_cards:
            if c.isEnabled():   # only close unsolved cards
                c.close_card()

        self.open_cards.clear()
        self.input_locked = False
        self.submit_btn.setDisabled(True)
    
    def close_open_cards(self):
        for c in self.open_cards:
            c.close_card()
        self.open_cards.clear()
        self.input_locked=False
        self.submit_btn.setDisabled(True)
    def submit_cards(self):
        if len(self.open_cards)!=3:
            return

        self.total_submits+=1

        values=[c.text().replace("\n"," ") for c in self.open_cards]
        key = frozenset(values)

        if key in self.valid_sets:
            self.correct_submits += 1

            explanation = self.explanations.get(key, "")
            self.show_explanation(explanation, "#93c5fd")

            for c in self.open_cards:
                c.setDisabled(True)
                c.setText("")
        else:
            self.show_explanation("Wrong combination", "#ef4444")

            for c in self.open_cards:
                c.close_card()

        self.open_cards.clear()
        self.input_locked=False
        self.submit_btn.setDisabled(True)

        remaining=[c for c in self.cards if c.isEnabled()]
        if len(remaining)==0:
            QTimer.singleShot(2500, self.end_full_game)

    def end_full_game(self):
        import time
        total_time=time.time()-self.start_time if self.start_time else 1

        accuracy=(self.correct_submits/self.total_submits) if self.total_submits>0 else 0

        difficulty=self.get_selected("difficulty")
        if difficulty=="Advanced": Ds=1.5
        elif difficulty=="Mixed": Ds=1.2
        else: Ds=1

        ref_rating = 100

        k = ref_rating / max(self.my_rating, 1)

        Ts = (max(total_time, 0.1) / 10) * (k / 2)

        Ds = max(Ds, 0.1)

        accuracy = max(0, accuracy)

        rating_add = (200 * accuracy) / (Ds * Ts) if Ts != 0 else 0

        rating_add = max(0, rating_add)

        self.my_rating += rating_add
        self.my_rating = round(self.my_rating)
        self.update_rating(self.my_rating)

        try:
            with open(self.save_path,"w") as f:
                f.write(str(self.my_rating))
        except:
            pass
        
        self.game_active = False
        self.end_game()

    # ================= HELPERS =================
    def divider(self):
        d=QFrame()
        d.setFixedHeight(1)
        d.setStyleSheet("background:#0f172a;")
        return d
    
    def panel(self,inner,bg):
        f=QFrame()
        f.setStyleSheet(f"background:{bg};border-radius:20px;")
        l=QVBoxLayout(f)
        l.setContentsMargins(16,16,16,16)
        l.addLayout(inner)
        return f
    
    def control_card(self,title,inner):
        f=QFrame()
        f.setStyleSheet("background:transparent;")
        l=QVBoxLayout(f)
        lbl=QLabel(title)
        lbl.setFont(QFont("Inter",20,QFont.Bold))
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color:#cbd5f5;")
        l.addWidget(lbl)
        l.addLayout(inner)
        return f
    
    def exclusive_buttons(self, names, key):
        layout = QGridLayout()
        layout.setSpacing(10)

        group = QButtonGroup(self)
        group.setExclusive(True)

        if not hasattr(self, "button_groups"):
            self.button_groups = {}

        self.button_groups[key] = group

        cols = 3   # 🔥 change this to control width (3 = perfect)

        for i, n in enumerate(names):
            b = QPushButton(n)
            b.setCheckable(True)

            b.setStyleSheet("""
            QPushButton{
                color:#94a3b8;
                padding:10px;
                border-radius:10px;
            }
            QPushButton:checked{
                background:#3b82f6;
                color:white;
            }
            """)

            if i == 0:
                b.setChecked(True)

            group.addButton(b)

            row = i // cols
            col = i % cols
            layout.addWidget(b, row, col)

        return layout
    
    # ================= RATING =================
    def update_rating(self,new_rating):
        self.my_rating=new_rating
        self.rating_label.setText(f"RATING\n{round(self.my_rating)}")

# ================= RUN =================
if __name__=="__main__":
    app=QApplication(sys.argv)
    w=ProjectXUI()
    w.show()
    sys.exit(app.exec())