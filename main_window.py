# main_window.py

import qtawesome as qta
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QFileDialog, QVBoxLayout, QGraphicsScene,
    QColorDialog, QAction, QActionGroup, QLabel, QSlider, QUndoStack,
    QSpinBox, QToolBar, QDockWidget, QFormLayout, QGroupBox, QHBoxLayout,
    QComboBox, QMenu, QSizePolicy, QToolButton, QGraphicsView, QUndoCommand,
    QButtonGroup
)
from PyQt5.QtGui import (
    QPixmap, QPainter, QImage, QColor, QFontDatabase, QKeySequence
)
from PyQt5.QtCore import Qt, QRectF, QSize, QPointF

# Import from our custom modules
from canvas_view import CanvasView
from commands import PropertyChangeCommand, DeleteCommand, AddCommand, GroupCommand, UngroupCommand
from graphics_items import ImageItem, TextItem, BaseItem, GroupItem

class ProfessionalEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graphics Editor")
        self.setGeometry(100, 100, 1600, 900)
        self.current_tool = 'select'
        self.undo_stack = QUndoStack(self)
        self.z_counter = 0
        self.zoom_levels = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 4.0, 8.0]
        self.clipboard = []

        # --- NEW: State for eyedropper ---
        self.is_picking_color = False
        self.picking_for_property = None

        self.setup_ui()
        self.setup_connections()
        self.set_tool('select')
        self.update_action_states()

    def setup_ui(self):
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-10000, -10000, 20000, 20000)
        self.scene.setBackgroundBrush(QColor("#f8f9fa"))
        self.view = CanvasView(self.scene, self)
        self.setCentralWidget(self.view)

        self.create_actions()
        self.create_tool_bar()
        self.create_inspector_panel()
        self.create_menu_bar()
        self.create_zoom_controls()

    def create_actions(self):
        self.undo_action = self.undo_stack.createUndoAction(self, "Undo"); self.undo_action.setShortcut(QKeySequence.Undo)
        self.redo_action = self.undo_stack.createRedoAction(self, "Redo"); self.redo_action.setShortcut(QKeySequence.Redo)
        self.copy_action = QAction(qta.icon('fa5s.copy', color='#333'), "Copy", self, triggered=self.copy_selection, shortcut=QKeySequence.Copy)
        self.paste_action = QAction(qta.icon('fa5s.paste', color='#333'), "Paste", self, triggered=self.paste_selection, shortcut=QKeySequence.Paste)
        self.duplicate_action = QAction(qta.icon('fa5s.clone', color='#333'), "Duplicate", self, triggered=self.duplicate_selection, shortcut=QKeySequence("Ctrl+D"))
        self.delete_action = QAction(qta.icon('fa5s.trash-alt', color='#d9534f'), "Delete", self, triggered=self.delete_selection, shortcut=QKeySequence.Delete)
        self.group_action = QAction(qta.icon('fa5s.object-group', color='#333'), "Group", self, triggered=self.group_selection, shortcut=QKeySequence("Ctrl+G"))
        self.ungroup_action = QAction(qta.icon('fa5s.object-ungroup', color='#333'), "Ungroup", self, triggered=self.ungroup_selection, shortcut=QKeySequence("Ctrl+Shift+G"))
        self.save_action = QAction("Save as PNG...", self, triggered=self.save_image)
        self.open_action = QAction("Import Image...", self, triggered=self.import_image)
        self.bring_to_front_action = QAction(qta.icon('fa5s.angle-double-up', color='#333'), "Bring to Front", self, triggered=self.bring_to_front)
        self.send_to_back_action = QAction(qta.icon('fa5s.angle-double-down', color='#333'), "Send to Back", self, triggered=self.send_to_back)
        self.bring_forward_action = QAction(qta.icon('fa5s.angle-up', color='#333'), "Bring Forward", self, triggered=self.bring_forward)
        self.send_backward_action = QAction(qta.icon('fa5s.angle-down', color='#333'), "Send Backward", self, triggered=self.send_backward)
        self.zoom_in_action = QAction("Zoom In", self, triggered=self.zoom_in); self.zoom_in_action.setShortcuts([QKeySequence("Ctrl++"), QKeySequence("Ctrl+=")])
        self.zoom_out_action = QAction("Zoom Out", self, triggered=self.zoom_out); self.zoom_out_action.setShortcut(QKeySequence("Ctrl+-"))
        self.reset_zoom_action = QAction("Reset Zoom to 100%", self, triggered=self.reset_zoom); self.reset_zoom_action.setShortcut(QKeySequence("Ctrl+0"))
        self.addAction(self.zoom_in_action); self.addAction(self.zoom_out_action); self.addAction(self.reset_zoom_action)

    def create_tool_bar(self):
        self.tool_bar = QToolBar("Tools")
        self.tool_bar.setIconSize(QSize(28, 28)); self.tool_bar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(Qt.TopToolBarArea, self.tool_bar); self.tool_bar.setMovable(False)
        self.tool_action_group = QActionGroup(self); self.tool_action_group.setExclusive(True)
        tools = [('select', 'fa5s.mouse-pointer', 'Select'), ('pan', 'fa5s.hand-paper', 'Pan'), None, ('rectangle', 'fa5s.square', 'Rectangle'), ('ellipse', 'fa5s.circle', 'Ellipse'), ('line', 'fa5s.minus', 'Line'), ('arrow', 'fa5s.long-arrow-alt-right', 'Arrow'), ('pencil', 'fa5s.pencil-alt', 'Pencil'), None, ('text_english', 'fa5s.align-left', 'EN Text'), ('text_urdu', 'fa5s.align-right', 'UR Text'), None, ('image', 'fa5s.image', 'Image'), ('eraser', 'fa5s.eraser', 'Eraser')]
        shortcuts = {'Select':'V', 'Pan':'H', 'Rectangle':'R', 'Ellipse':'O', 'Line':'L', 'Arrow':'A', 'Pencil':'P', 'EN Text':'T', 'Image':'I', 'Eraser':'E'}
        for tool_info in tools:
            if tool_info is None: self.tool_bar.addSeparator(); continue
            name, icon, text = tool_info
            action = QAction(qta.icon(icon, color='#333'), text, self); action.setData(name)
            tooltip_text = text
            if text in shortcuts:
                shortcut_key = shortcuts[text]
                action.setShortcut(QKeySequence(shortcut_key)); tooltip_text += f" ({shortcut_key})"
            action.setToolTip(tooltip_text)
            action.triggered.connect(lambda checked, n=name: self.set_tool(n)); action.setCheckable(True)
            self.tool_action_group.addAction(action); self.tool_bar.addAction(action)
            if name == 'select': action.setChecked(True)

    def create_inspector_panel(self):
        self.inspector_dock = QDockWidget("Properties", self)
        self.inspector_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.inspector_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.inspector_dock.setFixedWidth(350)
        panel_widget = QWidget()
        panel_widget.setObjectName("inspectorPanel")
        main_layout = QVBoxLayout(panel_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        appearance_box = QGroupBox("Appearance")
        form_layout1 = QFormLayout(appearance_box)
        self.stroke_row = QWidget()
        stroke_layout = QHBoxLayout(self.stroke_row)
        stroke_layout.setContentsMargins(0, 0, 0, 0); stroke_layout.setSpacing(5)
        self.stroke_color_btn = QPushButton(); self.stroke_color_btn.setProperty("class", "color-button")
        self.stroke_eyedropper_btn = QPushButton(qta.icon('fa5s.eye-dropper', color='#333'), ""); self.stroke_eyedropper_btn.setToolTip("Pick Stroke Color from Canvas"); self.stroke_eyedropper_btn.setFixedSize(34, 34)
        stroke_layout.addWidget(self.stroke_color_btn)
        stroke_layout.addWidget(self.stroke_eyedropper_btn)
        form_layout1.addRow("Stroke:", self.stroke_row)
        self.stroke_width_row = QWidget()
        h_layout = QHBoxLayout(self.stroke_width_row)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(QLabel("Thickness:"))
        self.stroke_width_input = QSpinBox(minimum=1, maximum=100)
        h_layout.addWidget(self.stroke_width_input)
        form_layout1.addRow(self.stroke_width_row)
        self.fill_row = QWidget()
        fill_layout = QHBoxLayout(self.fill_row)
        fill_layout.setContentsMargins(0, 0, 0, 0); fill_layout.setSpacing(5)
        self.fill_color_btn = QPushButton(); self.fill_color_btn.setProperty("class", "color-button")
        self.fill_eyedropper_btn = QPushButton(qta.icon('fa5s.eye-dropper', color='#333'), ""); self.fill_eyedropper_btn.setToolTip("Pick Fill Color from Canvas"); self.fill_eyedropper_btn.setFixedSize(34, 34)
        fill_layout.addWidget(self.fill_color_btn)
        fill_layout.addWidget(self.fill_eyedropper_btn)
        form_layout1.addRow("Fill:", self.fill_row)
        self.opacity_slider = QSlider(Qt.Horizontal, minimum=0, maximum=100)
        form_layout1.addRow("Opacity:", self.opacity_slider)
        self.text_box = QGroupBox("Text")
        form_layout2 = QFormLayout(self.text_box)
        self.font_family_combo = QComboBox(); self.font_family_combo.addItems(QFontDatabase().families())
        self.font_size_input = QSpinBox(minimum=8, maximum=500)
        self.text_color_btn = QPushButton(); self.text_color_btn.setProperty("class", "color-button")
        self.align_left_btn = QPushButton(qta.icon('fa5s.align-left', color='#333'), ""); self.align_left_btn.setToolTip("Align Left")
        self.align_center_btn = QPushButton(qta.icon('fa5s.align-center', color='#333'), ""); self.align_center_btn.setToolTip("Align Center")
        self.align_right_btn = QPushButton(qta.icon('fa5s.align-right', color='#333'), ""); self.align_right_btn.setToolTip("Align Right")
        self.align_justify_btn = QPushButton(qta.icon('fa5s.align-justify', color='#333'), ""); self.align_justify_btn.setToolTip("Justify")
        self.align_group = QButtonGroup(self); self.align_group.setExclusive(True)
        for i, btn in enumerate([self.align_left_btn, self.align_center_btn, self.align_right_btn, self.align_justify_btn]):
            btn.setCheckable(True); btn.setProperty("class", "format-button"); self.align_group.addButton(btn, i)
        self.bold_btn=QPushButton(qta.icon('fa5s.bold',color='#333'),"");self.bold_btn.setCheckable(True);self.bold_btn.setProperty("class","format-button")
        self.italic_btn=QPushButton(qta.icon('fa5s.italic',color='#333'),"");self.italic_btn.setCheckable(True);self.italic_btn.setProperty("class","format-button")
        self.underline_btn=QPushButton(qta.icon('fa5s.underline',color='#333'),"");self.underline_btn.setCheckable(True);self.underline_btn.setProperty("class","format-button")
        format_layout=QHBoxLayout(); format_layout.setSpacing(5)
        format_layout.addWidget(self.bold_btn); format_layout.addWidget(self.italic_btn); format_layout.addWidget(self.underline_btn)
        format_layout.addSpacing(10); format_layout.addWidget(self.align_left_btn); format_layout.addWidget(self.align_center_btn); format_layout.addWidget(self.align_right_btn); format_layout.addWidget(self.align_justify_btn)
        format_layout.addStretch()
        form_layout2.addRow("Font:", self.font_family_combo); form_layout2.addRow("Style:", format_layout)
        form_layout2.addRow("Size:", self.font_size_input); form_layout2.addRow("Color:", self.text_color_btn)
        main_layout.addWidget(appearance_box); main_layout.addWidget(self.text_box)
        main_layout.addStretch()
        self.inspector_dock.setWidget(panel_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.inspector_dock)
        self.inspector_dock.hide()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File"); file_menu.addAction(self.open_action); file_menu.addAction(self.save_action)
        edit_menu = menubar.addMenu("Edit"); edit_menu.addAction(self.undo_action); edit_menu.addAction(self.redo_action); edit_menu.addSeparator()
        edit_menu.addAction(self.copy_action); edit_menu.addAction(self.paste_action); edit_menu.addAction(self.duplicate_action); edit_menu.addSeparator(); edit_menu.addAction(self.delete_action)
        object_menu = menubar.addMenu("Object")
        object_menu.addAction(self.group_action); object_menu.addAction(self.ungroup_action)
        object_menu.addSeparator()
        object_menu.addAction(self.bring_to_front_action); object_menu.addAction(self.bring_forward_action); object_menu.addAction(self.send_backward_action); object_menu.addAction(self.send_to_back_action)
        view_menu = menubar.addMenu("View"); view_menu.addAction(self.zoom_in_action); view_menu.addAction(self.zoom_out_action); view_menu.addAction(self.reset_zoom_action)

    def create_zoom_controls(self):
        self.zoom_widget=QWidget(self,objectName="zoomPanel");layout=QHBoxLayout(self.zoom_widget);layout.setContentsMargins(5,5,5,5);layout.setSpacing(5);zoom_out_btn=QPushButton("-");zoom_out_btn.clicked.connect(self.zoom_out);self.zoom_button=QToolButton();self.zoom_button.setText("100%");self.zoom_button.setToolTip("Set zoom level");self.zoom_button.setPopupMode(QToolButton.InstantPopup);self.zoom_button.setFixedWidth(70);zoom_menu=QMenu(self);
        for level in self.zoom_levels:
            action=QAction(f"{int(level*100)}%",self);action.triggered.connect(lambda c,s=level:self.set_zoom_level(s));zoom_menu.addAction(action)
        zoom_menu.addSeparator();zoom_menu.addAction(self.reset_zoom_action);self.zoom_button.setMenu(zoom_menu);zoom_in_btn=QPushButton("+");zoom_in_btn.clicked.connect(self.zoom_in);layout.addWidget(zoom_out_btn);layout.addWidget(self.zoom_button);layout.addWidget(zoom_in_btn);self.zoom_widget.adjustSize()

    # --- FUNCTION MODIFIED ---
    def setup_connections(self):
        self.scene.selectionChanged.connect(self.update_inspector); self.scene.selectionChanged.connect(self.update_action_states)
        self.stroke_color_btn.clicked.connect(lambda: self.change_color_property('stroke'))
        self.fill_color_btn.clicked.connect(lambda: self.change_color_property('fill'))
        self.text_color_btn.clicked.connect(lambda: self.change_color_property('color'))
        self.opacity_slider.sliderPressed.connect(self.cache_opacity_change)
        self.opacity_slider.valueChanged.connect(lambda v: self.change_property('opacity', v, is_final=False))
        self.opacity_slider.sliderReleased.connect(self.finalize_opacity_change)
        self.font_size_input.editingFinished.connect(lambda: self.change_property('size', self.font_size_input.value()))
        self.stroke_width_input.editingFinished.connect(lambda: self.change_property('stroke_width', self.stroke_width_input.value()))
        self.font_family_combo.currentTextChanged.connect(lambda family: self.change_property('family', family))
        self.bold_btn.toggled.connect(lambda c: self.change_property('bold', c))
        self.italic_btn.toggled.connect(lambda c: self.change_property('italic', c))
        self.underline_btn.toggled.connect(lambda c: self.change_property('underline', c))
        self.align_group.buttonClicked[int].connect(self.change_text_alignment)

        # --- NEW: Eyedropper connections ---
        self.stroke_eyedropper_btn.clicked.connect(lambda: self.start_color_picking('stroke'))
        self.fill_eyedropper_btn.clicked.connect(lambda: self.start_color_picking('fill'))

    # --- NEW: Eyedropper methods ---
    def start_color_picking(self, target_property):
        item = self.get_selected()
        if not isinstance(item, (BaseItem, TextItem)):
            return

        self.is_picking_color = True
        self.picking_for_property = target_property
        self.view.setCursor(Qt.CrossCursor)

    def finish_color_picking(self, color):
        if not self.is_picking_color:
            return
        
        item = self.get_selected()
        prop = self.picking_for_property
        
        if item and prop and color.isValid():
            if prop == 'color': # Special case for text item's main color
                old_color = item.defaultTextColor()
            else: # For BaseItem stroke/fill
                old_color = getattr(item, f"{prop}_color", QColor())
            
            self.add_command(PropertyChangeCommand(item, prop, old_color, color))

        self.is_picking_color = False
        self.picking_for_property = None
        self.view.setCursor(Qt.ArrowCursor)
        self.set_tool('select')

    def change_text_alignment(self, button_id):
        item = self.get_selected()
        if not isinstance(item, TextItem): return
        alignment_map = {0: Qt.AlignLeft, 1: Qt.AlignCenter, 2: Qt.AlignRight, 3: Qt.AlignJustify}
        new_alignment = alignment_map.get(button_id)
        if new_alignment is not None and item.alignment != new_alignment:
            self.add_command(PropertyChangeCommand(item, 'alignment', item.alignment, new_alignment))

    def group_selection(self):
        selected = self.scene.selectedItems()
        if len(selected) > 1: self.add_command(GroupCommand(self.scene, selected))

    def ungroup_selection(self):
        selected = self.scene.selectedItems()
        groups = [item for item in selected if isinstance(item, GroupItem)]
        if groups:
            cmd = QUndoCommand("Ungroup Multiple"); [UngroupCommand(self.scene, g, parent=cmd) for g in groups]; self.add_command(cmd)

    def copy_selection(self):
        self.clipboard=[item.clone() for item in self.scene.selectedItems()]; self.update_action_states()

    def paste_selection(self):
        if not self.clipboard: return
        self.scene.clearSelection(); items_to_add=[]
        for item in self.clipboard:
            new_item=item.clone(); new_item.setPos(new_item.pos()+QPointF(20,20)); new_item.setSelected(True); items_to_add.append(new_item)
        cmd=QUndoCommand(); cmd.setText(f"Paste {len(items_to_add)} items"); [AddCommand(self.scene,i,parent=cmd) for i in items_to_add]; self.add_command(cmd)

    def duplicate_selection(self):
        selected_items=self.scene.selectedItems()
        if not selected_items: return
        self.scene.clearSelection(); items_to_add=[]
        for item in selected_items:
            new_item=item.clone(); new_item.setPos(item.pos()+QPointF(20,20)); new_item.setSelected(True); items_to_add.append(new_item)
        cmd=QUndoCommand(); cmd.setText(f"Duplicate {len(items_to_add)} items"); [AddCommand(self.scene,i,parent=cmd) for i in items_to_add]; self.add_command(cmd)

    def get_selected(self):
        selected=self.scene.selectedItems(); return selected[0] if len(selected)==1 else None

    def update_inspector(self, focused_item=None):
        item = focused_item if focused_item else self.get_selected()
        if item: self.inspector_dock.show()
        else: self.inspector_dock.hide(); return

        is_text = isinstance(item, TextItem)
        is_shape = isinstance(item, BaseItem)

        self.inspector_dock.setWindowTitle(f"{item.type_name()} Properties")
        self.text_box.setVisible(is_text)
        self.stroke_row.setVisible(is_shape)
        self.stroke_width_row.setVisible(is_shape)
        self.fill_row.setVisible(is_shape)
        
        self.opacity_slider.blockSignals(True); self.opacity_slider.setValue(int(item.opacity_val * 100)); self.opacity_slider.blockSignals(False)

        if is_text:
            font = item.font()
            self.font_family_combo.blockSignals(True); self.font_family_combo.setCurrentText(font.family()); self.font_family_combo.blockSignals(False)
            self.font_size_input.blockSignals(True); self.font_size_input.setValue(font.pointSize()); self.font_size_input.blockSignals(False)
            self.bold_btn.blockSignals(True); self.bold_btn.setChecked(font.bold()); self.bold_btn.blockSignals(False)
            self.italic_btn.blockSignals(True); self.italic_btn.setChecked(font.italic()); self.italic_btn.blockSignals(False)
            self.underline_btn.blockSignals(True); self.underline_btn.setChecked(font.underline()); self.underline_btn.blockSignals(False)
            self.text_color_btn.setStyleSheet(f"background-color: {item.defaultTextColor().name()};")
            alignment_map = {Qt.AlignLeft: 0, Qt.AlignCenter: 1, Qt.AlignRight: 2, Qt.AlignJustify: 3}
            btn_id = alignment_map.get(item.alignment)
            if btn_id is not None:
                self.align_group.blockSignals(True); self.align_group.button(btn_id).setChecked(True); self.align_group.blockSignals(False)

        if is_shape:
            self.stroke_width_input.blockSignals(True); self.stroke_width_input.setValue(item.stroke_width); self.stroke_width_input.blockSignals(False)
            self.stroke_color_btn.setStyleSheet(f"background-color: {item.stroke_color.name()};")
            fill_name = item.fill_color.name() if item.fill_color.alpha() > 0 else 'transparent'
            self.fill_color_btn.setStyleSheet(f"background-color: {fill_name};")

    def change_property(self, prop, new_val, is_final=True):
        item = self.get_selected()
        if not item: return
        if not is_final: item.set_property(prop, new_val); return
        old_val=None
        if prop=='size':old_val=item.font().pointSize()
        elif prop=='family':old_val=item.font().family()
        elif prop=='bold':old_val=item.font().bold()
        elif prop=='italic':old_val=item.font().italic()
        elif prop=='underline':old_val=item.font().underline()
        elif prop=='stroke_width':old_val=item.stroke_width
        if old_val is not None and old_val != new_val: self.add_command(PropertyChangeCommand(item,prop,old_val,new_val))

    def cache_opacity_change(self):
        if(item:=self.get_selected()):setattr(item,'_old_opacity',item.opacity_val*100)

    def finalize_opacity_change(self):
        if(item:=self.get_selected()) and hasattr(item,'_old_opacity'):
            new_opacity=item.opacity_val*100
            if item._old_opacity!=new_opacity:self.add_command(PropertyChangeCommand(item,'opacity',item._old_opacity,new_opacity))
            delattr(item,'_old_opacity')

    def change_color_property(self,prop_name):
        if not(item:=self.get_selected()):return
        is_text_color=prop_name=='color'
        old_color=item.defaultTextColor() if is_text_color else getattr(item,f"{prop_name}_color")
        if(new_color:=QColorDialog.getColor(old_color,self,f"Select Color")).isValid():
            self.add_command(PropertyChangeCommand(item,prop_name,old_color,new_color))

    # --- FUNCTION MODIFIED ---
    def set_tool(self, name):
        # Prevent changing tool while in the middle of picking a color
        if self.is_picking_color:
            return
        
        if name in['lock','image']:
            if name=='lock':self.toggle_lock_selected()
            if name=='image':self.import_image()
            self.tool_action_group.actions()[0].setChecked(True);return
        self.current_tool=name;drag_modes={'select':QGraphicsView.RubberBandDrag,'pan':QGraphicsView.ScrollHandDrag};cursors={'select':Qt.ArrowCursor,'pan':Qt.OpenHandCursor}
        self.view.setDragMode(drag_modes.get(name,QGraphicsView.NoDrag)); self.view.setCursor(cursors.get(name,Qt.CrossCursor))
        for action in self.tool_action_group.actions():
            if name==action.data():action.setChecked(True);break

    def update_action_states(self):
        selected_items = self.scene.selectedItems()
        has_selection = len(selected_items) > 0
        has_clipboard = len(self.clipboard) > 0
        self.group_action.setEnabled(len(selected_items) > 1)
        self.ungroup_action.setEnabled(any(isinstance(item, GroupItem) for item in selected_items))
        self.delete_action.setEnabled(has_selection); self.copy_action.setEnabled(has_selection)
        self.duplicate_action.setEnabled(has_selection); self.paste_action.setEnabled(has_clipboard)
        self.bring_to_front_action.setEnabled(has_selection); self.send_to_back_action.setEnabled(has_selection)
        self.bring_forward_action.setEnabled(has_selection); self.send_backward_action.setEnabled(has_selection)

    def bring_to_front(self):
        if not (items := self.scene.selectedItems()): return
        self.z_counter += 1
        for item in items: self.add_command(PropertyChangeCommand(item, 'zValue', item.zValue(), self.z_counter))
    def send_to_back(self):
        if not (items := self.scene.selectedItems()): return
        min_z = min((i.zValue() for i in self.scene.items()), default=0)
        for item in items: self.add_command(PropertyChangeCommand(item, 'zValue', item.zValue(), min_z - 1))
    def bring_forward(self):
        if not (item := self.get_selected()): return
        sorted_items = sorted(self.scene.items(), key=lambda i: i.zValue())
        try:
            idx = sorted_items.index(item)
            if idx < len(sorted_items) - 1:
                new_z = sorted_items[idx + 1].zValue() + 0.01; self.add_command(PropertyChangeCommand(item, 'zValue', item.zValue(), new_z))
        except ValueError: pass
    def send_backward(self):
        if not (item := self.get_selected()): return
        sorted_items = sorted(self.scene.items(), key=lambda i: i.zValue())
        try:
            idx = sorted_items.index(item)
            if idx > 0:
                new_z = sorted_items[idx - 1].zValue() - 0.01; self.add_command(PropertyChangeCommand(item, 'zValue', item.zValue(), new_z))
        except ValueError: pass
    def toggle_lock_selected(self):
        if(items:=self.scene.selectedItems()):
            target_lock_state = not items[0].locked
            for item in items: self.add_command(PropertyChangeCommand(item,'locked',item.locked, target_lock_state))
    def set_zoom_level(self, scale):
        current_scale = self.view.transform().m11()
        if abs(current_scale) < 1e-9: return
        factor = scale / current_scale; self.view.scale(factor, factor); self.update_zoom_display()
    def zoom_in(self):
        current_scale=self.view.transform().m11();next_level=next((l for l in self.zoom_levels if l>current_scale+0.01),None)
        if next_level:self.set_zoom_level(next_level)
        else:self.view.scale(1.2,1.2);self.update_zoom_display()
    def zoom_out(self):
        current_scale=self.view.transform().m11();prev_level=next((l for l in reversed(self.zoom_levels) if l<current_scale-0.01),None)
        if prev_level:self.set_zoom_level(prev_level)
        else:self.view.scale(1/1.2,1.2);self.update_zoom_display()
    def reset_zoom(self): self.set_zoom_level(1.0)
    def update_zoom_display(self):
        scale=self.view.transform().m11()
        for level in self.zoom_levels:
            if abs(scale/level-1)<0.015:self.zoom_button.setText(f"{int(level*100)}%");return
        self.zoom_button.setText(f"{scale*100:.0f}%")
    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,'zoom_widget'):sz=self.zoom_widget.sizeHint();self.zoom_widget.move(self.width()-sz.width()-15,self.height()-sz.height()-15)
    def add_command(self,command): self.undo_stack.push(command)
    def keyPressEvent(self,event):
        if event.key() == Qt.Key_Escape and self.is_picking_color:
            self.finish_color_picking(QColor()) # Cancel picking with an invalid color
        elif not event.isAutoRepeat() and event.key()==Qt.Key_Space: 
            self._last_tool=self.current_tool; self.set_tool('pan')
    def keyReleaseEvent(self,event):
        if not event.isAutoRepeat() and event.key()==Qt.Key_Space and hasattr(self,'_last_tool'): self.set_tool(self._last_tool)
    def import_image(self):
        path,_=QFileDialog.getOpenFileName(self,"Import Image","","Images (*.png *.jpg *.jpeg)")
        if path:
            pixmap=QPixmap(path)
            if pixmap.isNull(): return
            item=ImageItem(pixmap);self.add_command(AddCommand(self.scene,item));item_bounds=item.sceneBoundingRect()
            padded_bounds=item_bounds.adjusted(-item_bounds.width()*0.05,-item_bounds.height()*0.05,item_bounds.width()*0.05,item_bounds.height()*0.05)
            self.view.fitInView(padded_bounds,Qt.KeepAspectRatio);self.update_zoom_display()
    def save_image(self):
        bounds = self.scene.itemsBoundingRect()
        if not bounds.isValid(): return
        path, _ = QFileDialog.getSaveFileName(self, "Save Image", "untitled.png", "PNG (*.png)")
        if not path: return
        self.scene.clearSelection();image = QImage(bounds.size().toSize(), QImage.Format_ARGB32_Premultiplied);image.fill(Qt.transparent)
        painter=QPainter(image);painter.setRenderHint(QPainter.Antialiasing);self.scene.render(painter,QRectF(image.rect()),bounds);painter.end();image.save(path)
    def delete_selection(self):
        if(items:=self.scene.selectedItems()): self.add_command(DeleteCommand(self.scene,items))