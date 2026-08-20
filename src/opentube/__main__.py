import sys

from PySide6.QtWidgets import QApplication

from opentube.ui.windows.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    
    # Token-based stylesheet mapping to the precise visual design.
    # BG_SIDEBAR: #151515
    # BG_MAIN: #212121
    # SURFACE_1: #1C1C1C
    # SURFACE_2: #242424
    # BORDER: #333333
    
    app.setStyleSheet("""
        /* GLOBAL TYPOGRAPHY */
        QWidget {
            font-family: "Stack Sans", "Segoe UI", sans-serif;
            font-size: 14px;
            color: #FFFFFF;
        }

        /* WORKSPACE & SIDEBAR */
        #Workspace {
            background-color: #212121;
        }
        #Sidebar {
            background-color: #151515;
            border-right: 1px solid #282828;
        }
        
        #LogoIcon {
            font-size: 20px;
            color: #FFFFFF;
        }
        #LogoText {
            font-size: 20px;
            font-weight: 600;
            color: #FFFFFF;
        }

        /* SIDEBAR NAVIGATION */
        #SidebarButton, #SidebarButtonActive {
            background-color: transparent;
            color: #B3B3B3;
            text-align: left;
            padding: 12px 16px;
            border: none;
            border-radius: 6px;
            font-weight: 500;
        }
        #SidebarButton:hover {
            background-color: #1C1C1C;
            color: #FFFFFF;
        }
        #SidebarButtonActive {
            background-color: #212121;
            color: #FFFFFF;
        }

        /* INPUTS */
        QLineEdit {
            padding: 10px 16px;
            background-color: #1C1C1C;
            color: #FFFFFF;
            border: 1px solid #333333;
            border-radius: 6px;
            selection-background-color: #555555;
        }
        QLineEdit:focus {
            border: 1px solid #555555;
        }

        /* BUTTONS */
        QPushButton {
            font-weight: 500;
        }
        
        #FetchButton, #PrimaryButton {
            background-color: #FFFFFF;
            color: #151515;
            border: none;
            border-radius: 6px;
            font-weight: 600;
        }
        #FetchButton:hover, #PrimaryButton:hover {
            background-color: #E0E0E0;
        }
        #FetchButton:pressed, #PrimaryButton:pressed {
            background-color: #CCCCCC;
        }
        #FetchButton:disabled, #PrimaryButton:disabled {
            background-color: #404040;
            color: #808080;
        }

        #SecondaryButton {
            background-color: #242424;
            color: #FFFFFF;
            border: 1px solid #383838;
            border-radius: 6px;
        }
        #SecondaryButton:hover {
            background-color: #2C2C2C;
        }
        #SecondaryButton:pressed {
            background-color: #333333;
        }

        /* SEGMENTED CONTROL */
        #SegmentLeft {
            background-color: #181818;
            color: #B3B3B3;
            border: 1px solid #333333;
            border-top-left-radius: 6px;
            border-bottom-left-radius: 6px;
            border-right: none;
        }
        #SegmentRight {
            background-color: #181818;
            color: #B3B3B3;
            border: 1px solid #333333;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
            border-left: none;
        }
        #SegmentLeft:checked, #SegmentRight:checked {
            background-color: #FFFFFF;
            color: #151515;
            font-weight: 600;
        }

        /* CARDS */
        #MetaCard, #ActionCard {
            background-color: #1C1C1C;
            border: 1px solid #333333;
            border-radius: 8px;
        }

        #ThumbnailPlaceholder {
            background-color: #151515;
            border: 1px solid #282828;
            border-radius: 6px;
        }

        /* TEXT STYLES */
        #SectionTitle {
            font-size: 16px;
            font-weight: 600;
            color: #FFFFFF;
        }
        #FieldLabel {
            font-size: 13px;
            font-weight: 500;
            color: #B3B3B3;
        }
        #MetaTitle {
            font-size: 18px;
            font-weight: 600;
            color: #FFFFFF;
        }
        #MetaUploader {
            font-size: 14px;
            color: #B3B3B3;
        }
        #MetaDuration {
            font-size: 13px;
            color: #808080;
        }
        #StatusLabel {
            font-size: 14px;
            color: #B3B3B3;
        }

        /* FORMAT LIST (SCROLL AREA) */
        #FormatsScroll {
            background-color: transparent;
            border: none;
        }
        #FormatsContent {
            background-color: transparent;
        }

        /* FORMAT ROW */
        #FormatRow {
            background-color: #181818;
            border: 1px solid #333333;
            border-radius: 8px;
        }
        #FormatRow:hover {
            background-color: #1C1C1C;
            border: 1px solid #404040;
        }
        #FormatRow[selected="true"] {
            background-color: #242424;
            border: 1px solid #FFFFFF;
        }

        #FormatTitle {
            font-size: 15px;
            font-weight: 600;
            color: #FFFFFF;
        }
        #FormatSubtitle {
            font-size: 13px;
            color: #808080;
        }
        #FormatRightText {
            font-size: 14px;
            color: #B3B3B3;
        }
        
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 2px solid #555555;
            background-color: transparent;
        }
        QRadioButton::indicator:checked {
            border: 2px solid #FFFFFF;
            background-color: #151515;
        }
        /* Create a fake inner dot for radio */
        QRadioButton::indicator:checked:pressed {
             background-color: #FFFFFF;
        }

        /* PROGRESS BAR */
        QProgressBar {
            border: none;
            border-radius: 3px;
            background-color: #282828;
            text-align: center;
            color: transparent;
        }
        QProgressBar::chunk {
            background-color: #FFFFFF;
            border-radius: 3px;
        }

        /* SCROLLBAR */
        QScrollBar:vertical {
            border: none;
            background: #212121;
            width: 8px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical {
            background: #404040;
            min-height: 20px;
            border-radius: 4px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
