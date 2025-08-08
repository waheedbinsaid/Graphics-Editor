# canvas_view.py
from PyQt5.QtWidgets import QGraphicsView, QMenu
from PyQt5.QtGui import QPainter, QPen, QPainterPath
from PyQt5.QtCore import Qt, QRectF, QLineF
import qtawesome as qta

# Import our custom classes
from commands import AddCommand, DeleteCommand
from graphics_items import TextItem, RectangleItem, EllipseItem, LineItem, ArrowItem, FreehandItem

class CanvasView(QGraphicsView):
    def __init__(self, scene, editor):
        super().__init__(scene)
        self.editor = editor
        self.start_pos = None
        self.temp_item = None
        self.current_path = None
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def mousePressEvent(self, event):
        # --- NEW: Handle eyedropper picking ---
        if self.editor.is_picking_color:
            pixmap = self.grab()
            image = pixmap.toImage()
            color = image.pixelColor(event.pos())
            self.editor.finish_color_picking(color)
            return  # Stop further processing

        tool = self.editor.current_tool
        if event.button() == Qt.LeftButton and tool not in ['select', 'pan']:
            self.start_pos = self.mapToScene(event.pos())
            if tool in ['text_urdu', 'text_english']:
                lang = 'urdu' if tool == 'text_urdu' else 'english'
                item = TextItem(lang)
                item.setPos(self.start_pos)
                self.editor.add_command(AddCommand(self.scene(), item))
                self.scene().clearSelection()
                item.setSelected(True)
                item.setFocus()
                self.editor.set_tool('select')
            elif tool == 'pencil':
                self.current_path = QPainterPath()
                self.current_path.moveTo(self.start_pos)
            elif tool == 'eraser':
                self.erase_at(self.start_pos)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.start_pos and self.editor.current_tool not in ['select', 'pan']:
            current_pos = self.mapToScene(event.pos())
            if self.temp_item: self.scene().removeItem(self.temp_item)
            tool = self.editor.current_tool
            pen = QPen(Qt.gray, 2, Qt.DashLine)
            if tool == 'pencil':
                self.current_path.lineTo(current_pos)
                self.temp_item = self.scene().addPath(self.current_path, pen)
            elif tool == 'eraser':
                self.erase_at(current_pos)
            elif tool in ['line', 'arrow']:
                self.temp_item = self.scene().addLine(QLineF(self.start_pos, current_pos), pen)
            else:
                self.temp_item = self.scene().addRect(QRectF(self.start_pos, current_pos).normalized(), pen)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.start_pos and event.button() == Qt.LeftButton and self.editor.current_tool not in ['select', 'pan', 'text_urdu', 'text_english']:
            if self.temp_item: self.scene().removeItem(self.temp_item)
            end_pos = self.mapToScene(event.pos())
            rect = QRectF(self.start_pos, end_pos).normalized()
            item_map = {
                'rectangle': RectangleItem(rect),
                'ellipse': EllipseItem(rect),
                'line': LineItem(QLineF(self.start_pos, end_pos)),
                'arrow': ArrowItem(QLineF(self.start_pos, end_pos)),
                'pencil': FreehandItem(self.current_path) if self.current_path else None
            }
            if (new_item := item_map.get(self.editor.current_tool)):
                self.editor.add_command(AddCommand(self.scene(), new_item))
            self.editor.set_tool('select')
        self.start_pos = None
        self.temp_item = None
        self.current_path = None
        super().mouseReleaseEvent(event)

    def erase_at(self, pos):
        if (items_to_erase := [item for item in self.scene().items(pos) if not getattr(item, 'locked', False)]):
            self.editor.add_command(DeleteCommand(self.scene(), items_to_erase))

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
            self.scale(factor, factor)
            self.editor.update_zoom_display()
        else:
            super().wheelEvent(event)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if not item:
            super().contextMenuEvent(event)
            return

        if not item.isSelected():
            self.scene().clearSelection()
            item.setSelected(True)

        menu = QMenu(self)
        layer_menu = menu.addMenu(qta.icon('fa5s.layer-group', color='#333'), "Layer")
        layer_menu.addAction(self.editor.bring_to_front_action)
        layer_menu.addAction(self.editor.bring_forward_action)
        layer_menu.addAction(self.editor.send_backward_action)
        layer_menu.addAction(self.editor.send_to_back_action)
        menu.addSeparator()

        if hasattr(item, 'locked'):
            is_locked = item.locked
            lock_text = "Unlock" if is_locked else "Lock"
            lock_icon = qta.icon('fa5s.lock', color='#333') if is_locked else qta.icon('fa5s.unlock', color='#333')
            from PyQt5.QtWidgets import QAction
            lock_action = QAction(lock_icon, lock_text, self)
            lock_action.triggered.connect(self.editor.toggle_lock_selected)
            menu.addAction(lock_action)

        menu.addAction(self.editor.delete_action)
        menu.exec_(event.globalPos())