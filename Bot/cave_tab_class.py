import time
from funkcje import *


class CaveTab(QWidget):
    def __init__(self):
        super().__init__()

        self.waypoints_list = QListWidget(self)
        self.waypoints_list.setGeometry(0, 20, 170, 200)

        label_text = QLabel("Waypoints", self)
        label_text.setGeometry(0, 0, 100, 20)

        self.save_wpt_list = QListWidget(self)
        self.save_wpt_list.setGeometry(300, 320, 120, 80)
        for file in os.listdir("Waypoints"):
            self.save_wpt_list.addItem(f"{file.split('.')[0]}")

        self.save_wpt_text = QLabel("Name", self)
        self.save_wpt_text.setGeometry(301, 400, 100, 20)

        self.save_wpt_textfield = QLineEdit(self)
        self.save_wpt_textfield.setGeometry(335, 401, 85, 20)

        self.save_wpt_button = QPushButton("Save", self)
        self.save_wpt_button.setGeometry(334, 421, 41, 20)
        self.save_wpt_button.clicked.connect(self.save_waypoints_list)

        self.load_wpt_button = QPushButton("Load", self)
        self.load_wpt_button.setGeometry(380, 421, 41, 20)
        self.load_wpt_button.clicked.connect(self.load_waypoints_list)

        self.delete_wpt_button = QPushButton("Del", self)
        self.delete_wpt_button.setGeometry(299, 421, 31, 20)
        self.delete_wpt_button.clicked.connect(self.delete_list)

        left = QPushButton("<", self)
        left.setGeometry(0, 220, 30, 25)
        right = QPushButton(">", self)
        right.setGeometry(31, 220, 30, 25)

        del_waypoint = QPushButton("Del", self)
        del_waypoint.setGeometry(111, 220, 40, 25)
        del_waypoint.clicked.connect(self.delete_wpt_item)

        clear_waypoint = QPushButton("Clear", self)
        clear_waypoint.setGeometry(66, 220, 40, 25)
        clear_waypoint.clicked.connect(self.clear_wpt_list)

        cave_status = QCheckBox(self)
        cave_status.move(0, 260)
        cave_status_text = QLabel("Follow Waypoints", self)
        cave_status_text.setGeometry(17, 251, 100, 30)

        stand = QPushButton("Stand", self)
        stand.setGeometry(200, 20, 40, 25)
        stand.clicked.connect(self.stand_add)

        north = QPushButton("North", self)
        north.setGeometry(241, 20, 40, 25)
        north.clicked.connect(self.north_add)

        action = QPushButton("Action", self)
        action.setGeometry(282, 20, 40, 25)

        south = QPushButton("South", self)
        south.setGeometry(241, 46, 40, 25)
        south.clicked.connect(self.south_add)

        west = QPushButton("West", self)
        west.setGeometry(200, 46, 40, 25)

        east = QPushButton("East", self)
        east.setGeometry(282, 46, 40, 25)

        auto_rec_label = QLabel("Auto Recording", self)
        auto_rec_label.setGeometry(17, 281, 100, 30)
        auto_rec_box = QCheckBox(self)
        auto_rec_box.move(0, 290)

        def start_auto_rec_thread():
            autorec_thread = Thread(target=auto_rec)
            autorec_thread.daemon = True  # Daemonize the thread to terminate it when the main thread exits
            if auto_rec_box.checkState() == 2:
                autorec_thread.start()

        auto_rec_box.stateChanged.connect(start_auto_rec_thread)

        def start_follow_thread():
            follow_wpt_thread = Thread(target=follow_wpt)
            follow_wpt_thread.daemon = True  # Daemonize the thread to terminate it when the main thread exits
            if cave_status.checkState() == 2:
                follow_wpt_thread.start()

        cave_status.stateChanged.connect(start_follow_thread)

        def auto_rec():
            new_x = 0
            new_y = 0
            new_z = 0
            while auto_rec_box.checkState():
                x = read_memory(my_x, base_adr, 0, procID)
                y = read_memory(my_y, base_adr, 0, procID)
                z = read_memory(my_z, base_adr, 0, procID)
                x = c.c_int.from_buffer(x).value
                y = c.c_int.from_buffer(y).value
                z = c.c_int.from_buffer(z).value
                if (x != new_x or y != new_y) and z == new_z:
                    self.waypoints_list.addItem('I-X:'f'{x} Y:'f'{y} Z:'f'{z}')
                if z != new_z:
                    if y > new_y:
                        self.waypoints_list.addItem('S-X:'f'{x} Y:'f'{y} Z:'f'{z}')
                    elif y < new_y:
                        self.waypoints_list.addItem('N-X:'f'{x} Y:'f'{y} Z:'f'{z}')
                new_x = x
                new_y = y
                new_z = z
                time.sleep(0.2)

        def follow_wpt():
            while cave_status.checkState():
                for i in range(0, self.waypoints_list.count()):
                    status = self.waypoints_list.item(i).text().split("-")[0]
                    numbers = re.sub(r'\D', ' ', self.waypoints_list.item(i).text())
                    wpt = [num for num in numbers.split(' ') if num]
                    self.waypoints_list.setCurrentRow(i)
                    while cave_status.checkState():
                        targetID = read_memory(attack, base_adr, 0, procID)
                        targetID = c.c_ulonglong.from_buffer(targetID).value
                        while targetID != 0:
                            targetID = read_memory(attack, base_adr, 0, procID)
                            targetID = c.c_ulonglong.from_buffer(targetID).value
                            time.sleep(2)
                        time.sleep(0.1)
                        x = read_memory(my_x, base_adr, 0, procID)
                        y = read_memory(my_y, base_adr, 0, procID)
                        z = read_memory(my_z, base_adr, 0, procID)
                        x = c.c_int.from_buffer(x).value
                        y = c.c_int.from_buffer(y).value
                        z = c.c_int.from_buffer(z).value
                        if x == int(wpt[0]) and y == int(wpt[1]) and z == int(wpt[2]):
                            break
                        else:
                            if status == 'I':
                                go_stand(wpt[0], wpt[1], wpt[2], x, y, z)
                                continue
                            if status == 'N':
                                go_north(wpt[0], wpt[1], wpt[2], x, y, z)
                                continue
                            if status == 'S':
                                go_south(wpt[0], wpt[1], wpt[2], x, y, z)
                                continue


    def delete_wpt_item(self):
        selected_item = self.waypoints_list.currentItem()
        if selected_item:
            self.waypoints_list.takeItem(self.waypoints_list.row(selected_item))

    def clear_wpt_list(self):
        self.waypoints_list.clear()

    def delete_list(self):
        selected_item = self.save_wpt_list.currentItem()
        if selected_item:
            os.remove(
                'Waypoints/'f'{self.save_wpt_list.item(self.save_wpt_list.row(selected_item)).text()}.txt')
            self.save_wpt_list.takeItem(self.save_wpt_list.row(selected_item))

    def save_waypoints_list(self):
        if self.save_wpt_textfield.text() != '':
            f = open("Waypoints/"f"{self.save_wpt_textfield.text()}.txt", "w")
            self.save_wpt_list.addItem(f'{self.save_wpt_textfield.text()}')
            self.save_wpt_textfield.clear()
            for i in range(self.waypoints_list.count()):
                f.write(f'{self.waypoints_list.item(i).text()}\n')
            f.close()

    def load_waypoints_list(self):
        self.waypoints_list.clear()
        selected_item = self.save_wpt_list.currentItem()
        if selected_item:
            f = open(
                "Waypoints/"f"{self.save_wpt_list.item(self.save_wpt_list.row(selected_item)).text()}.txt")
            for wpt in f:
                if wpt != '\n':
                    self.waypoints_list.addItem(wpt.split('\n')[0])
            f.close()

    def stand_add(self):
        x = read_memory(my_x, base_adr, 0, procID)
        y = read_memory(my_y, base_adr, 0, procID)
        z = read_memory(my_z, base_adr, 0, procID)
        x = c.c_int.from_buffer(x).value
        y = c.c_int.from_buffer(y).value
        z = c.c_int.from_buffer(z).value
        self.waypoints_list.addItem('I-X:'f'{x} Y:'f'{y} Z:'f'{z}')

    def north_add(self):
        x = read_memory(my_x, base_adr, 0, procID)
        y = read_memory(my_y, base_adr, 0, procID)
        z = read_memory(my_z, base_adr, 0, procID)
        x = c.c_int.from_buffer(x).value
        y = c.c_int.from_buffer(y).value
        z = c.c_int.from_buffer(z).value
        self.waypoints_list.addItem('N-X:'f'{x} Y:'f'{y} Z:'f'{z}')

    def south_add(self):
        x = read_memory(my_x, base_adr, 0, procID)
        y = read_memory(my_y, base_adr, 0, procID)
        z = read_memory(my_z, base_adr, 0, procID)
        x = c.c_int.from_buffer(x).value
        y = c.c_int.from_buffer(y).value
        z = c.c_int.from_buffer(z).value
        self.waypoints_list.addItem('S-X:'f'{x} Y:'f'{y} Z:'f'{z}')
