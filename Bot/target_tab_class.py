from funkcje import *


class TargetTab(QWidget):
    def __init__(self, parent=None):
        super(TargetTab, self).__init__(parent)
        # Labels
        targeting_list_label = QLabel("Targeting List", self)
        targeting_list_label.setGeometry(0, 0, 200, 20)

        monster_name = QLabel("Monster ", self)
        monster_name.setGeometry(160, 20, 50, 20)

        save_targeting_text = QLabel("Name", self)
        save_targeting_text.setGeometry(301, 400, 100, 20)

        save_targeting_text = QLabel("Name", self)
        save_targeting_text.setGeometry(301, 400, 100, 20)

        # List Widgets
        self.targeting_list_ListWidget = QListWidget(self)
        self.targeting_list_ListWidget.setGeometry(0, 20, 150, 200)

        self.save_targeting_list = QListWidget(self)
        self.save_targeting_list.setGeometry(300, 320, 120, 80)
        for file in os.listdir("Targeting"):
            self.save_targeting_list.addItem(f"{file.split('.')[0]}")

        # Line Edits
        self.save_targeting_textfield = QLineEdit(self)
        self.save_targeting_textfield.setGeometry(335, 401, 85, 20)

        self.textfield = QLineEdit(self)
        self.textfield.setGeometry(210, 20, 100, 20)

        # Push Buttons
        self.save_targeting_button = QPushButton("Save", self)
        self.save_targeting_button.setGeometry(334, 421, 41, 20)
        self.save_targeting_button.clicked.connect(self.save_monster_list)

        self.load_targeting_button = QPushButton("Load", self)
        self.load_targeting_button.setGeometry(380, 421, 41, 20)
        self.load_targeting_button.clicked.connect(self.load_monster_list)

        self.delete_targeting_button = QPushButton("Del", self)
        self.delete_targeting_button.setGeometry(299, 421, 31, 20)
        self.delete_targeting_button.clicked.connect(self.delete_list)

        add_monster = QPushButton("Add", self)
        add_monster.setGeometry(209, 40, 40, 25)
        add_monster.clicked.connect(self.create_monster)

        left = QPushButton("<", self)
        left.setGeometry(0, 220, 30, 25)
        left.clicked.connect(self.go_left)

        right = QPushButton(">", self)
        right.setGeometry(31, 220, 30, 25)
        right.clicked.connect(self.go_right)

        del_monster = QPushButton("Del", self)
        del_monster.setGeometry(111, 220, 40, 25)
        del_monster.clicked.connect(self.delete_monster)

        clear_monsters = QPushButton("Clear", self)
        clear_monsters.setGeometry(66, 220, 40, 25)
        clear_monsters.clicked.connect(self.clear_monster_list)

        # Check Boxes
        loot_status = QCheckBox(self)
        loot_status.move(0, 401)
        loot_status_text = QLabel("Start Looting", self)
        loot_status_text.setGeometry(17, 391, 100, 30)

        target_status = QCheckBox(self)
        target_status.move(0, 420)
        target_status_text = QLabel("Start Targeting", self)
        target_status_text.setGeometry(17, 411, 100, 30)

        def list_monsters_thread():
            fnt = ImageFont.truetype("./Tahoma.ttf", 15)
            background_color = (0, 0, 0)
            thread = Thread(target=list_monsters)
            thread.daemon = True  # Daemonize the thread to terminate it when the main thread exits
            if target_status.checkState() == 2:
                for i in range(self.monster_list.count()):
                    image = Image.new('RGB', (8*len(self.monster_list.item(i).text()), 20), background_color)
                    draw = ImageDraw.Draw(image)
                    draw.multiline_text((0, 0), self.monster_list.item(i).text(), font=fnt, fill=(219, 127, 62))
                    opencv_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
                    cv.imwrite('Monsters/'+self.monster_list.item(i).text()+'.png', opencv_image)
                    draw.rectangle([(10, 10), (150, 30)], fill=background_color)
                thread.start()

        target_status.stateChanged.connect(list_monsters_thread)

        def list_monsters():
            win_cap = WindowCapture('Medivia', 675, 675, 525, 150)
            bgr_color = np.uint8([[[138, 148, 255]]])
            hsv_color = cv.cvtColor(bgr_color, cv.COLOR_BGR2HSV)
            lower = np.array([hsv_color[0][0][0] - 10, 180, 145])
            upper = np.array([hsv_color[0][0][0] + 10, 185, 255])
            while target_status.checkState() == 2:
                for i in range(self.monster_list.count()):
                    monster = self.monster_list.item(i).text()
                    if [x for x in os.listdir('Monsters/') if x.split('.')[0] == monster]:
                        locations = [(0, 0)]
                        time.sleep(0.1)
                        while locations:
                            with lock:
                                img = win_cap.get_screenshot()
                                hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
                                mask = cv.inRange(hsv, lower, upper)
                                result = cv.bitwise_and(img, img, mask=mask)
                                template = cv.imread('Monsters/'f'{monster}' + '.png')
                                result = cv.matchTemplate(result, template, cv.TM_CCOEFF_NORMED)
                                locations = list(zip(*(np.where(result >= 0.5)[::-1])))
                                if locations:
                                    locations = merge_close_points(locations, 10)
                                    locations = sorted(locations, key=sort_monsters_by_distance)
                                    monsterX, monsterY = locations[0]
                                    value = read_memory(attack, 0)
                                    value = c.c_ulonglong.from_buffer(value).value
                                    if not value:
                                        click_right(int(monsterX) + 545, int(monsterY) + 180)
                                    time.sleep(0.3)
                            time.sleep(0.1)

    def delete_list(self):
        selected_item = self.save_targeting_list.currentItem()
        if selected_item:
            os.remove(
                'Targeting/'f'{self.save_targeting_list.item(self.save_targeting_list.row(selected_item)).text()}.txt')
            self.save_targeting_list.takeItem(self.save_targeting_list.row(selected_item))

    def clear_monster_list(self):
        self.monster_list.clear()

    def save_monster_list(self):
        if self.save_targeting_textfield.text() != '':
            f = open("Targeting/"f"{self.save_targeting_textfield.text()}.txt", "w")
            self.save_targeting_list.addItem(f'{self.save_targeting_textfield.text()}')
            self.save_targeting_textfield.clear()
            for i in range(self.monster_list.count()):
                f.write(f'{self.monster_list.item(i).text()}\n')
            f.close()

    def load_monster_list(self):
        self.monster_list.clear()
        selected_item = self.save_targeting_list.currentItem()
        if selected_item:
            f = open(
                "Targeting/"f"{self.save_targeting_list.item(self.save_targeting_list.row(selected_item)).text()}.txt")
            for monster in f:
                if monster != '\n':
                    self.monster_list.addItem(monster.split("\n")[0])
            f.close()

    def delete_monster(self):
        selected_item = self.monster_list.currentItem()
        if selected_item:
            self.monster_list.takeItem(self.monster_list.row(selected_item))

    def create_monster(self):
        if self.textfield.text() != '':
            self.targeting_list_ListWidget.addItem(self.textfield.text())
            self.textfield.clear()

    def go_right(self):
        self.monster_list.setCurrentRow(self.monster_list.currentRow() + 1)

    def go_left(self):
        self.monster_list.setCurrentRow(self.monster_list.currentRow() - 1)

