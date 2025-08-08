# graphics_items.py
import math
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem, QGraphicsPixmapItem, QGraphicsItemGroup, QStyle
from PyQt5.QtGui import QColor, QPen, QPainterPath, QPolygonF, QFont, QPixmap, QTextCursor, QTextBlockFormat
from PyQt5.QtCore import Qt, QRectF, QPointF

class GroupItem(QGraphicsItemGroup):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)
        self.setCursor(Qt.OpenHandCursor); self.opacity_val = 1.0; self.locked = False
    def type_name(self): return "Group"
    def set_property(self, name, value):
        if name == 'opacity': self.opacity_val = value / 100.0; self.setOpacity(self.opacity_val)
        elif name == 'locked': self.locked = value; self.setFlag(self.ItemIsMovable, not value)
        elif name == 'zValue': self.setZValue(value)
    def paint(self, painter, option, widget=None):
        if option.state & QStyle.State_Selected:
            pen = QPen(QColor("#0078d4"), 2, Qt.DashLine)
            painter.setPen(pen); painter.setBrush(Qt.NoBrush); painter.drawRect(self.boundingRect())

class BaseItem(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.setFlags(self.ItemIsSelectable | self.ItemIsMovable | self.ItemSendsGeometryChanges)
        self.setCursor(Qt.OpenHandCursor)
        self.stroke_color, self.fill_color = QColor("#343a40"), QColor(Qt.transparent)
        self.stroke_width = 4; self.opacity_val, self.locked = 1.0, False
    def type_name(self): return "Shape"
    def set_property(self, name, value):
        prop_map = { 'stroke': lambda v: setattr(self, 'stroke_color', v), 'fill': lambda v: setattr(self, 'fill_color', v), 'opacity': lambda v: setattr(self, 'opacity_val', v / 100.0), 'stroke_width': lambda v: setattr(self, 'stroke_width', v), 'locked': lambda v: (setattr(self, 'locked', v), self.setFlag(self.ItemIsMovable, not v)), 'zValue': self.setZValue }
        if name in prop_map:
            prop_map[name](value); self.prepareGeometryChange(); self.update()
    def paint_setup(self, painter):
        painter.setOpacity(self.opacity_val)
        pen = QPen(self.stroke_color, self.stroke_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen); painter.setBrush(self.fill_color)
    def clone(self):
        constructor_arg = self.rect if hasattr(self, 'rect') else (self.line if hasattr(self, 'line') else (self.path if hasattr(self, 'path') else None))
        new_item = type(self)(constructor_arg)
        new_item.stroke_color = QColor(self.stroke_color); new_item.fill_color = QColor(self.fill_color)
        new_item.stroke_width = self.stroke_width; new_item.opacity_val = self.opacity_val; new_item.setZValue(self.zValue())
        return new_item

class RectangleItem(BaseItem):
    def __init__(self, rect): super().__init__(); self.rect = rect
    def boundingRect(self): return self.rect.adjusted(-self.stroke_width/2, -self.stroke_width/2, self.stroke_width/2, self.stroke_width/2)
    def type_name(self): return "Rectangle"
    def paint(self, painter, option, widget):
        self.paint_setup(painter); painter.drawRect(self.rect)
        if option.state & QStyle.State_Selected:
            pen = QPen(QColor("#0078d4"), 2, Qt.DashLine)
            painter.setPen(pen); painter.setBrush(Qt.NoBrush); painter.drawRect(self.boundingRect())

class EllipseItem(BaseItem):
    def __init__(self, rect): super().__init__(); self.rect = rect
    def boundingRect(self): return self.rect.adjusted(-self.stroke_width/2, -self.stroke_width/2, self.stroke_width/2, self.stroke_width/2)
    def type_name(self): return "Ellipse"
    def paint(self, painter, option, widget):
        self.paint_setup(painter); painter.drawEllipse(self.rect)
        if option.state & QStyle.State_Selected:
            pen = QPen(QColor("#0078d4"), 2, Qt.DashLine)
            painter.setPen(pen); painter.setBrush(Qt.NoBrush); painter.drawRect(self.boundingRect())

class LineItem(BaseItem):
    def __init__(self, line): super().__init__(); self.line = line
    def boundingRect(self): return QRectF(self.line.p1(), self.line.p2()).normalized().adjusted(-self.stroke_width, -self.stroke_width, self.stroke_width, self.stroke_width)
    def type_name(self): return "Line"
    def paint(self, painter, option, widget):
        self.paint_setup(painter); painter.drawLine(self.line)
        if option.state & QStyle.State_Selected:
            pen = QPen(QColor("#0078d4"), 2, Qt.DashLine)
            painter.setPen(pen); painter.setBrush(Qt.NoBrush); painter.drawRect(self.boundingRect())

class ArrowItem(LineItem):
    def type_name(self): return "Arrow"
    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        arrowhead_size = 6 + self.stroke_width * 2
        angle = math.atan2(-self.line.dy(), self.line.dx())
        p1 = self.line.p2() + QPointF(math.sin(angle-math.pi/3)*arrowhead_size, math.cos(angle-math.pi/3)*arrowhead_size)
        p2 = self.line.p2() + QPointF(math.sin(angle-math.pi+math.pi/3)*arrowhead_size, math.cos(angle-math.pi+math.pi/3)*arrowhead_size)
        painter.setBrush(self.stroke_color); painter.setPen(QPen(self.stroke_color)); painter.drawPolygon(QPolygonF([self.line.p2(), p1, p2]))

class FreehandItem(BaseItem):
    def __init__(self, path): super().__init__(); self.path = path
    def boundingRect(self): return self.path.boundingRect().adjusted(-self.stroke_width, -self.stroke_width, self.stroke_width, self.stroke_width)
    def type_name(self): return "Drawing"
    def paint(self, painter, option, widget):
        self.paint_setup(painter); painter.drawPath(self.path)
        if option.state & QStyle.State_Selected:
            pen = QPen(QColor("#0078d4"), 2, Qt.DashLine)
            painter.setPen(pen); painter.setBrush(Qt.NoBrush); painter.drawRect(self.boundingRect())

class TextItem(QGraphicsTextItem):
    def __init__(self, language='urdu'):
        super().__init__()
        self.setFlags(self.ItemIsSelectable | self.ItemIsMovable | self.ItemIsFocusable)
        self.setTextInteractionFlags(Qt.TextEditorInteraction); self.setCursor(Qt.IBeamCursor)
        self.opacity_val, self.locked, self.language = 1.0, False, language
        font = QFont("Jameel Noori Nastaleeq", 50) if language == 'urdu' else QFont("Segoe UI", 36)
        self.setFont(font)
        self.setPlainText("اردو میں لکھیں" if language == 'urdu' else "Type here")
        self.setDefaultTextColor(QColor("#343a40"))
        
        # --- NEW: Set and apply initial alignment ---
        self.alignment = Qt.AlignRight if language == 'urdu' else Qt.AlignLeft
        self.apply_alignment(self.alignment)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if self.scene() and self.scene().views():
            self.scene().views()[0].editor.update_inspector(focused_item=self)

    def type_name(self): return f"{self.language.capitalize()} Text"
    
    # --- NEW: Method to apply alignment ---
    def apply_alignment(self, alignment):
        self.alignment = alignment
        block_fmt = QTextBlockFormat()
        block_fmt.setAlignment(self.alignment)
        cursor = QTextCursor(self.document())
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(block_fmt)
        self.prepareGeometryChange()
        self.update()

    def set_property(self, name, value):
        font = self.font()
        prop_map = {
            'color': self.setDefaultTextColor, 'opacity': lambda v: setattr(self, 'opacity_val', v / 100.0),
            'size': lambda v: font.setPointSize(v), 'family': lambda v: font.setFamily(v),
            'bold': lambda v: font.setBold(v), 'italic': lambda v: font.setItalic(v),
            'underline': lambda v: font.setUnderline(v), 'locked': lambda v: (setattr(self, 'locked', v), self.setFlag(self.ItemIsMovable, not v)),
            'zValue': self.setZValue, 'alignment': self.apply_alignment
        }
        if name in prop_map:
            prop_map[name](value)
            if name not in ['color', 'opacity', 'locked', 'zValue', 'alignment']: self.setFont(font)
            self.update()

    def paint(self, painter, option, widget):
        painter.setOpacity(self.opacity_val)
        if option.state & QStyle.State_Selected:
            option.state &= ~QStyle.State_Selected
        super().paint(painter, option, widget)
        if self.isSelected():
            pen = QPen(QColor("#0078d4"), 2, Qt.DashLine)
            painter.setPen(pen); painter.setBrush(Qt.NoBrush); painter.drawRect(self.boundingRect())

    def clone(self):
        new_item = TextItem(self.language)
        new_item.setPlainText(self.toPlainText())
        new_item.setFont(self.font())
        new_item.setDefaultTextColor(self.defaultTextColor())
        new_item.opacity_val = self.opacity_val
        new_item.setZValue(self.zValue())
        # --- NEW: Copy alignment to clone ---
        new_item.apply_alignment(self.alignment)
        return new_item

class ImageItem(QGraphicsPixmapItem):
    def __init__(self, pixmap):
        super().__init__(pixmap); self.setFlags(self.ItemIsSelectable | self.ItemIsMovable)
        self.setCursor(Qt.OpenHandCursor); self.opacity_val, self.locked = 1.0, False
    def type_name(self): return "Image"
    def set_property(self, name, value):
        prop_map = {'opacity': lambda v: setattr(self, 'opacity_val', v/100.0), 'locked': lambda v: (setattr(self, 'locked', v), self.setFlag(self.ItemIsMovable, not v)), 'zValue': self.setZValue }
        if name in prop_map: prop_map[name](value); self.update()
    def paint(self, painter, option, widget):
        painter.setOpacity(self.opacity_val); super().paint(painter, option, widget)
        if option.state & QStyle.State_Selected:
            pen = QPen(QColor("#0078d4"), 2, Qt.DashLine)
            painter.setPen(pen); painter.setBrush(Qt.NoBrush); painter.drawRect(self.boundingRect())
    def clone(self):
        new_item = ImageItem(QPixmap(self.pixmap()))
        new_item.opacity_val = self.opacity_val; new_item.setZValue(self.zValue())
        return new_item