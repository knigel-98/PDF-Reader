import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QLabel, QScrollArea, QSpinBox, QLineEdit,
                             QToolBar, QStatusBar, QDialog, QTextEdit, QRubberBand)
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor
import fitz

class CommentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Comment")
        self.setGeometry(300, 300, 400, 200)
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CE PDF Viewer")
        self.setGeometry(100, 100, 1200, 800)

        # Create toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        # Create status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Create controls layout
        controls_layout = QHBoxLayout()

        # Navigation buttons
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)

        # Page number display and total pages
        self.page_spin = QSpinBox()
        self.page_spin.setPrefix("Page ")
        self.page_spin.valueChanged.connect(self.page_changed)
        self.total_pages_label = QLabel("of 0")

        # Zoom controls
        self.zoom_spin = QSpinBox()
        self.zoom_spin.setRange(25, 500)
        self.zoom_spin.setValue(100)
        self.zoom_spin.setSuffix("%")
        self.zoom_spin.valueChanged.connect(self.zoom_changed)

        # Search controls
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search text...")
        self.search_input.returnPressed.connect(self.search_text)
        self.search_prev = QPushButton("◀")
        self.search_next = QPushButton("▶")
        self.search_prev.clicked.connect(lambda: self.search_text(False))
        self.search_next.clicked.connect(lambda: self.search_text(True))

        # Add feature buttons
        self.add_comment_btn = QPushButton("Add comments")
        self.add_comment_btn.clicked.connect(self.add_comment)
        self.send_comment_btn = QPushButton("Send for comments")
        self.send_comment_btn.clicked.connect(self.send_for_comments)
        self.fill_sign_btn = QPushButton("Fill & Sign")
        self.fill_sign_btn.clicked.connect(self.fill_and_sign)
        self.edit_pdf_btn = QPushButton("Edit a PDF")
        self.edit_pdf_btn.clicked.connect(self.edit_pdf)
        self.export_pdf_btn = QPushButton("Export a PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        self.ai_assistant_btn = QPushButton("AI Assistant")
        self.ai_assistant_btn.clicked.connect(self.ai_assistant)
        self.gen_summary_btn = QPushButton("Generative summary")
        self.gen_summary_btn.clicked.connect(self.generate_summary)
        self.create_pdf_btn = QPushButton("Create a PDF")
        self.create_pdf_btn.clicked.connect(self.create_pdf)
        self.combine_files_btn = QPushButton("Combine files")
        self.combine_files_btn.clicked.connect(self.combine_files)
        self.share_btn = QPushButton("Share")
        self.share_btn.clicked.connect(self.share_pdf)
        self.add_stamp_btn = QPushButton("Add a stamp")
        self.add_stamp_btn.clicked.connect(self.add_stamp)
        self.measure_btn = QPushButton("Measure objects")
        self.measure_btn.clicked.connect(self.measure_objects)

        # Add controls to layout
        controls_layout.addWidget(QPushButton("Open", clicked=self.open_pdf))
        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.page_spin)
        controls_layout.addWidget(self.total_pages_label)
        controls_layout.addWidget(self.next_button)
        controls_layout.addWidget(QLabel("Zoom:"))
        controls_layout.addWidget(self.zoom_spin)
        controls_layout.addWidget(self.search_input)
        controls_layout.addWidget(self.search_prev)
        controls_layout.addWidget(self.search_next)

        # Create feature buttons layout
        features_layout = QHBoxLayout()
        features_layout.addWidget(self.add_comment_btn)
        features_layout.addWidget(self.send_comment_btn)
        features_layout.addWidget(self.fill_sign_btn)
        features_layout.addWidget(self.edit_pdf_btn)
        features_layout.addWidget(self.export_pdf_btn)
        features_layout.addWidget(self.ai_assistant_btn)
        features_layout.addWidget(self.gen_summary_btn)
        features_layout.addWidget(self.create_pdf_btn)
        features_layout.addWidget(self.combine_files_btn)
        features_layout.addWidget(self.share_btn)
        features_layout.addWidget(self.add_stamp_btn)
        features_layout.addWidget(self.measure_btn)

        # Create scroll area for PDF pages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Create label for displaying PDF pages
        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.page_label)

        # Add all widgets to main layout
        main_layout.addLayout(controls_layout)
        main_layout.addLayout(features_layout)
        main_layout.addWidget(self.scroll_area)

        # Initialize variables
        self.current_pdf = None
        self.current_page = 0
        self.zoom_factor = 1.0
        self.search_results = []
        self.current_search_index = -1
        self.measuring_mode = False
        self.rubber_band = None
        self.origin = QPoint()

    def open_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open PDF file", "", "PDF files (*.pdf)")
        if file_name:
            self.current_pdf = fitz.open(file_name)
            self.page_spin.setRange(1, len(self.current_pdf))
            self.total_pages_label.setText(f"of {len(self.current_pdf)}")
            self.show_page(0)

    def show_page(self, page_number):
        if self.current_pdf and 0 <= page_number < len(self.current_pdf):
            page = self.current_pdf[page_number]
            zoom = self.zoom_spin.value() / 100.0
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            self.page_label.setPixmap(pixmap)
            self.current_page = page_number
            self.page_spin.setValue(page_number + 1)

    def prev_page(self):
        if self.current_page > 0:
            self.show_page(self.current_page - 1)

    def next_page(self):
        if self.current_pdf and self.current_page < len(self.current_pdf) - 1:
            self.show_page(self.current_page + 1)

    def page_changed(self, value):
        self.show_page(value - 1)

    def zoom_changed(self, value):
        self.show_page(self.current_page)

    def search_text(self, forward=True):
        if not self.current_pdf:
            return

        search_text = self.search_input.text()
        if not search_text:
            return

        if not self.search_results:
            # New search
            self.search_results = []
            self.current_search_index = -1
            for page_num in range(len(self.current_pdf)):
                page = self.current_pdf[page_num]
                results = page.search_for(search_text)
                for rect in results:
                    self.search_results.append((page_num, rect))

        if self.search_results:
            if forward:
                self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
            else:
                self.current_search_index = (self.current_search_index - 1) % len(self.search_results)

            page_num, _ = self.search_results[self.current_search_index]
            self.show_page(page_num)

    def add_comment(self):
        if not self.current_pdf:
            self.statusbar.showMessage("Please open a PDF first")
            return
        dialog = CommentDialog(self)
        if dialog.exec():
            comment = dialog.text_edit.toPlainText()
            self.statusbar.showMessage(f"Comment added: {comment}")

    def send_for_comments(self):
        if not self.current_pdf:
            self.statusbar.showMessage("Please open a PDF first")
            return
        self.statusbar.showMessage("Sending for comments...")

    def fill_and_sign(self):
        if not self.current_pdf:
            self.statusbar.showMessage("Please open a PDF first")
            return
        self.statusbar.showMessage("Fill & Sign mode activated")

    def edit_pdf(self):
        if not self.current_pdf:
            self.statusbar.showMessage("Please open a PDF first")
            return
        self.statusbar.showMessage("Edit mode activated")

    def export_pdf(self):
        if not self.current_pdf:
            self.statusbar.showMessage("Please open a PDF first")
            return
        file_name, _ = QFileDialog.getSaveFileName(self, "Export PDF", "", "PDF files (*.pdf)")
        if file_name:
            self.statusbar.showMessage(f"Exporting PDF to {file_name}")

    def ai_assistant(self):
        self.statusbar.showMessage("AI Assistant activated")

    def generate_summary(self):
        if not self.current_pdf:
            self.statusbar.showMessage("Please open a PDF first")
            return
        self.statusbar.showMessage("Generating summary...")

    def create_pdf(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Create PDF", "", "PDF files (*.pdf)")
        if file_name:
            self.statusbar.showMessage(f"Creating new PDF: {file_name}")

    def combine_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDFs to combine", "", "PDF files (*.pdf)")
        if files:
            self.statusbar.showMessage(f"Combining {len(files)} PDF files")

    def share_pdf(self):
        if not self.current_pdf:
            self.statusbar.showMessage("Please open a PDF first")
            return
        self.statusbar.showMessage("Opening share dialog...")

    def add_stamp(self):
        if not self.current_pdf:
            self.statusbar.showMessage("Please open a PDF first")
            return
        self.statusbar.showMessage("Add stamp mode activated")

    def measure_objects(self):
        if not self.current_pdf:
            self.statusbar.showMessage("Please open a PDF first")
            return
        self.measuring_mode = not self.measuring_mode
        if self.measuring_mode:
            self.statusbar.showMessage("Measure mode activated - Click and drag to measure")
            self.page_label.mousePressEvent = self.measure_press
            self.page_label.mouseMoveEvent = self.measure_move
            self.page_label.mouseReleaseEvent = self.measure_release
        else:
            self.statusbar.showMessage("Measure mode deactivated")
            self.page_label.mousePressEvent = None
            self.page_label.mouseMoveEvent = None
            self.page_label.mouseReleaseEvent = None

    def measure_press(self, event):
        self.origin = event.pos()
        if not self.rubber_band:
            self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self.page_label)
        self.rubber_band.setGeometry(QRect(self.origin, QSize()))
        self.rubber_band.show()

    def measure_move(self, event):
        if self.rubber_band:
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def measure_release(self, event):
        if self.rubber_band:
            rect = self.rubber_band.geometry()
            # Convert pixels to document units (e.g., mm or inches)
            self.statusbar.showMessage(f"Measured area: {rect.width()}x{rect.height()} pixels")
            self.rubber_band.hide()

def main():
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()