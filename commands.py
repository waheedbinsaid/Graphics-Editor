# commands.py
from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtCore import QPointF

from graphics_items import GroupItem

class AddCommand(QUndoCommand):
    def __init__(self, scene, item, text="", parent=None):
        super().__init__(text, parent)
        self.scene = scene
        self.item = item
        self.editor = self.scene.views()[0].editor
        if not text:
            self.setText(f"Add {item.type_name()}")

    def undo(self):
        self.scene.removeItem(self.item)
        self.editor.update_action_states()

    def redo(self):
        self.item.setZValue(self.editor.z_counter)
        self.scene.addItem(self.item)
        self.editor.z_counter += 1
        self.editor.update_action_states()

class DeleteCommand(QUndoCommand):
    def __init__(self, scene, items):
        super().__init__("Delete Selection")
        self.scene, self.items = scene, items
    def undo(self):
        for item in self.items: self.scene.addItem(item)
    def redo(self):
        for item in self.items: self.scene.removeItem(item)

class PropertyChangeCommand(QUndoCommand):
    def __init__(self, item, prop, old, new):
        super().__init__(f"Change {prop.replace('_', ' ').capitalize()}")
        self.item, self.prop, self.old, self.new = item, prop, old, new
    def _apply(self, val):
        self.item.set_property(self.prop, val)
        if self.item.scene() and self.item.scene().views():
            self.item.scene().views()[0].editor.update_inspector()
    def undo(self): self._apply(self.old)
    def redo(self): self._apply(self.new)

class GroupCommand(QUndoCommand):
    def __init__(self, scene, items_to_group):
        super().__init__("Group Items")
        self.scene = scene
        self.items = items_to_group
        self.group = GroupItem()

    def redo(self):
        self.scene.clearSelection()
        for item in self.items:
            item.setPos(item.mapToParent(item.pos()))
            self.group.addToGroup(item)

        self.scene.addItem(self.group)
        self.group.setSelected(True)

    def undo(self):
        self.scene.destroyItemGroup(self.group)
        for item in self.items:
            item.setSelected(True)

class UngroupCommand(QUndoCommand):
    # --- FIX: Added 'parent=None' to the constructor ---
    def __init__(self, scene, group_to_ungroup, parent=None):
        # --- And passed 'parent' to the superclass constructor ---
        super().__init__("Ungroup Items", parent)
        self.scene = scene
        self.group = group_to_ungroup
        self.children_items = []
        for item in self.group.childItems():
            self.children_items.append(item)

    def redo(self):
        self.scene.clearSelection()
        items = self.group.childItems()
        self.scene.destroyItemGroup(self.group)
        for item in items:
            item.setSelected(True)

    def undo(self):
        self.scene.clearSelection()
        for item in self.children_items:
            item.setPos(item.mapToParent(item.pos()))
            self.group.addToGroup(item)

        self.scene.addItem(self.group)
        self.group.setSelected(True)
