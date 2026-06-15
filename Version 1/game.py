import sys,random, csv
from PySide6.QtWidgets import (QApplication,QWidget,QLabel,QPushButton,QVBoxLayout,QHBoxLayout,QFrame,QGridLayout,QStackedWidget,QButtonGroup)
from PySide6.QtCore import Qt,QTimer
from PySide6.QtGui import QFont

# ================= CARD =================
class FlipCard(QPushButton):
    def __init__(self,parent):
        super().__init__()
        self.parent_ui=parent
        self.value=None
        self.is_open=False
        self.setFixedSize(92,122)
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
            border:2px solid #3b82f6;
            border-radius:16px;
            color:#94a3b8;
        }
        """
        self.face_style="""
        QPushButton{
            background:#0b1229;
            border:2px solid #60a5fa;
            border-radius:16px;
            color:white;
            font-size:10px;
            font-weight:bold;
            padding:4px;
        }
        QPushButton{
            qproperty-alignment: AlignCenter;
        }
        """
        # QPushButton{
#     background:#0b1229;
#     border:2px solid #60a5fa;
#     border-radius:16px;
#     color:white;
#     font-size:16px;
#     font-weight:bold;
# }
# """
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
        self.resize(1220,520)
        self.game_active=False
        self.open_cards=[]
        self.input_locked=False
        self.data = []

        try:
            with open("data.csv", newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 5:
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
            with open("rating.txt","r") as f:
                self.my_rating=int(f.read().strip())
        except:
            pass
        self.build_ui()
        
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
    # ================= PAGE SWITCH =================
    def switch_page(self,index):
        self.pages.setCurrentIndex(index)
        self.btn_dashboard.setProperty("selected",index==0)
        self.btn_game.setProperty("selected",index==1)
        for b in (self.btn_dashboard,self.btn_game):
            b.style().unpolish(b)
            b.style().polish(b)
            
    # ================= DASHBOARD =================
    def dashboard_page(self):
        from PySide6.QtWidgets import QGraphicsBlurEffect
        from PySide6.QtGui import QPixmap, QFont
        from PySide6.QtCore import Qt
 
        page = QFrame()
        page.setStyleSheet("background:#01030a;")

        width = 2000
        height = 1000

        # Background image
        bg = QLabel(page)
        bg.setGeometry(0,0,width,height)

        pix = QPixmap("Background.png")

        if pix.width() < width or pix.height() < height:
            pix = pix.scaled(
                width,
                height,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

        bg.setPixmap(pix)
        bg.setAlignment(Qt.AlignCenter)
        bg.setAttribute(Qt.WA_TransparentForMouseEvents)
        

        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(120)

        bg.setGraphicsEffect(blur)
        bg.lower()

        # Dark overlay
        overlay = QFrame(page)
        overlay.setGeometry(0,0,width,height)

        overlay.setStyleSheet(
            "background-color:rgba(2,6,23,220);"
        )
        overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        overlay.raise_()

        outer = QVBoxLayout(page)
        outer.addStretch()

        # Main glass box
        box = QFrame()
        box.setObjectName("mainbox")   # important
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

        # PROJECT X (no border)
        hero = QLabel("TESMEE")

        hero.setFont(QFont("Inter",56,QFont.Black))
        hero.setAlignment(Qt.AlignCenter)

        hero.setStyleSheet("""
        color:white;
        background:transparent;
        border:none;
        """)

        box_layout.addWidget(hero)

        # Rating card (keeps border intentionally)
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

        box_layout.addWidget(self.rating_label,alignment=Qt.AlignCenter)

        box_layout.addWidget(self.divider())

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
                self.exclusive_buttons(["Mathematics","Science","Mixed"], "topic")
            )
        )

        box_layout.addLayout(controls)

        box_layout.addWidget(self.divider())

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

        outer.addWidget(box,alignment=Qt.AlignHCenter)

        outer.addStretch()

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
        layout.addLayout(btn_row)
        return page
    # ================= GAME LOGIC =================
    def get_selected(self, key):
        group = self.button_groups.get(key)
        if not group:
            return None
        
        for btn in group.buttons():
            if btn.isChecked():
                return btn.text()
        
        return None
    
    def start_game(self):
        self.game_active = True
        self.input_locked = False
        self.open_cards.clear()
        self.combination_pool.clear()

        difficulty = self.get_selected("difficulty")
        topic = self.get_selected("topic")

        valid_combinations = []

        # 🔹 FILTER CSV PROPERLY
        for row in self.data:
            clue1, clue2, clue3, difficulty_csv, topic_csv = [x.strip() for x in row]

            if difficulty and difficulty != "Mixed":
                if difficulty.lower() != difficulty_csv.lower():
                    continue

            if topic and topic != "Mixed":
                if topic.lower() != topic_csv.lower():
                    continue

            valid_combinations.append([clue1, clue2, clue3])

        if len(valid_combinations) < 10:
            print("NOT ENOUGH COMBINATIONS")
            return

        # 🔹 PICK 10 RANDOM COMBINATIONS
        random.shuffle(valid_combinations)
        selected = valid_combinations[:10]

        self.valid_sets=set()
        for combo in selected:
            self.valid_sets.add(frozenset(combo))

        # 🔹 FLATTEN → 30 VALUES
        pool = []
        for combo in selected:
            pool.extend(combo)

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
            self.my_rating -= 5
            self.update_rating(self.my_rating)

            try:
                with open("rating.txt","w") as f:
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

        if frozenset(values) in self.valid_sets:
            self.correct_submits+=1
            for c in self.open_cards:
                c.setDisabled(True)
                c.setText("")
        else:
            for c in self.open_cards:
                c.close_card()

        self.open_cards.clear()
        self.input_locked=False
        self.submit_btn.setDisabled(True)

        remaining=[c for c in self.cards if c.isEnabled()]
        if len(remaining)==0:
            self.end_full_game()

    def end_full_game(self):
        import time
        total_time=time.time()-self.start_time if self.start_time else 1

        accuracy=(self.correct_submits/self.total_submits) if self.total_submits>0 else 0

        difficulty=self.get_selected("difficulty")
        if difficulty=="Advanced": Ds=1
        elif difficulty=="Mixed": Ds=1.2
        else: Ds=1.5

        base=self.my_rating
        k=base/self.my_rating if self.my_rating!=0 else 1
        Ts=(total_time/10)*(k/2)

        rating_add=(200*accuracy)/(Ds*Ts) if Ts!=0 else 0

        self.my_rating+=int(rating_add)
        self.update_rating(self.my_rating)

        try:
            with open("rating.txt","w") as f:
                f.write(str(self.my_rating))
        except:
            pass

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
        layout = QHBoxLayout()
        group = QButtonGroup(self)
        group.setExclusive(True)

        if not hasattr(self, "button_groups"):
            self.button_groups = {}

        self.button_groups[key] = group

        for i, n in enumerate(names):
            b = QPushButton(n)
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
            b.setCheckable(True)

            if i == 0:
                b.setChecked(True)

            group.addButton(b)
            layout.addWidget(b)

        layout.addStretch()
        return layout
    
    # ================= RATING =================
    def update_rating(self,new_rating):
        self.my_rating=new_rating
        self.rating_label.setText(f"RATING\n{self.my_rating}")

# ================= RUN =================
if __name__=="__main__":
    app=QApplication(sys.argv)
    w=ProjectXUI()
    w.show()
    sys.exit(app.exec())
