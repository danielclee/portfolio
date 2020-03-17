#ifndef WIN32_GUI
#define WIN32_GUI

///#include <windows.h> /* Basic Window commands */

namespace POS
{
  namespace GUI
  {
    class Win32Gui
    {
      public:
      Win32Gui();
      virtual ~Win32Gui();
  
      void ShowTestDialog();
      void ShowTestDialog2();

      void GetControls();

    };
  }
}






////#define WIN32_WINNT 0x0600 /* Keep for compatibility issues */
////
////#include <windows.h> /* Basic Window commands */
////#include <iostream> /* I/O stream commands */
////#include "resource.h"
////
////#define NUM_BTN 2 /* Number of hover buttons */
////
////HWND BtnHWND [NUM_BTN]; /* This is an array containing the HWND to the hover buttons. */
////BOOL bGUIAppDone = false; /* This controls the flow of the message loop. */
////WNDPROC DefaultBtnProc; /* Default PROC for buttons. */
////LPCSTR HoverBtnText; /* Hover button information string. */ 
////HWND hWndDlg; /* Window Handle of the Dialog */
////HINSTANCE hInstance; /* Hinstance. */
////
////INT CALLBACK DialogProc(HWND hwndDlg, UINT uMsg, WPARAM wParam, LPARAM lParam); 
////INT CALLBACK BtnProc(HWND hwndBtn, UINT uMsg, WPARAM wParam, LPARAM lParam); 
////void SetDialogBkColor(HWND hwndDlg, COLORREF TheColor); 
////void SetBtnProc(HWND hwnd); 
////void SetBtnInfo(HWND BtnHwnd);
////
////void OnClickMe(); /* When user clicks on “Click Me” button, execute this .*/
////
/////*************************************************************************/
////
////void SetDialogBkColor(HWND hwndDlg, COLORREF TheColor) 
//// { 
//// HDC hdc = GetDC(hwndDlg); 
//// HBRUSH DlgBkBrush = CreateSolidBrush(TheColor); 
//// RECT DlgRect; 
//// GetClientRect(hwndDlg, &DlgRect); 
//// HPEN MyPen = CreatePen(PS_SOLID, 1, TheColor); 
//// SelectObject(hdc,MyPen); 
//// SelectObject(hdc,DlgBkBrush); 
//// Rectangle(hdc,DlgRect.left, DlgRect.top, DlgRect.right, DlgRect.bottom); 
//// ReleaseDC(hwndDlg, hdc); 
//// DeleteObject(DlgBkBrush); 
//// DeleteObject(MyPen); 
//// UpdateWindow(hwndDlg); 
//// }
////
/////*************************************************************************/
////
////INT CALLBACK DialogProc(HWND hwndDlg, UINT uMsg, WPARAM wParam, LPARAM lParam) 
//// { 
//// /* Used to repaint the window. */
//// RECT DlgRect; 
//// HDC hdc = GetDC(hwndDlg); 
//// 
//// switch(uMsg) 
//// { 
//// /*Process MouseClicks. */
//// case(WM_COMMAND): 
//// 
//// switch(LOWORD(wParam)) 
//// {
//// case IDC_EXIT: 
//// DestroyWindow(hwndDlg); 
//// bGUIAppDone=TRUE; 
//// return TRUE; 
//// break; 
//// } 
//// 
//// break; 
//// case (WM_CTLCOLORSTATIC): 
//// { 
//// HBRUSH BgBrush = CreateSolidBrush(RGB(255,255,255)); 
//// return (int)BgBrush; 
//// } 
//// break; 
//// case (WM_ERASEBKGND): 
//// 
//// GetClientRect(hwndDlg, &DlgRect); 
//// SetDialogBkColor(hwndDlg, RGB(255,255,255)); 
//// InvalidateRect(hwndDlg, &DlgRect, FALSE) ; 
//// return TRUE; 
//// break; 
//// case (WM_CLOSE): 
//// DestroyWindow(hwndDlg); 
//// return TRUE; 
//// break; 
//// 
//// case (WM_DESTROY): 
//// bGUIAppDone=TRUE; 
//// return TRUE; 
//// break; 
//// } 
//// return 0; 
//// }
////
/////*************************************************************************/
////
/////* Button PROC. */
////INT CALLBACK BtnProc(HWND hwndBtn, UINT uMsg, WPARAM wParam, LPARAM lParam) 
//// { 
//// BOOL doTrack = true; 
//// /* If Mouse moves on button, set the hover text. */
//// if(uMsg == WM_MOUSEMOVE) 
//// { 
//// doTrack = false; 
//// SetBtnInfo(hwndBtn); 
//// SetWindowText(GetDlgItem(GetParent(hwndBtn),IDC_INFO), HoverBtnText); 
//// } 
//// /* Track mouse. */
//// TRACKMOUSEEVENT TrkMouseEvent; 
//// TrkMouseEvent.cbSize=sizeof(TrkMouseEvent); 
//// TrkMouseEvent.dwFlags = TME_LEAVE | TME_HOVER; 
//// TrkMouseEvent.dwHoverTime = 0; 
//// TrkMouseEvent.hwndTrack = hwndBtn; 
//// if(!doTrack) 
//// TrackMouseEvent(&TrkMouseEvent); 
//// /* Set the appropriate hover text. */
//// SetBtnInfo(hwndBtn); 
//// /* Set hover text if mouse hovers. */
//// if(uMsg == WM_MOUSEHOVER) 
//// SetWindowText(GetDlgItem(GetParent(hwndBtn),IDC_INFO), HoverBtnText); 
//// 
//// /* Reset default hover text when mouse leaves.*/
//// if(uMsg == WM_MOUSELEAVE) 
//// { 
//// SetWindowText(GetDlgItem(GetParent(hwndBtn),IDC_INFO), "Welcome …"); 
//// doTrack=false; 
//// } 
//// /* Call default PROC to manage other messages. */
//// return CallWindowProc( DefaultBtnProc, hwndBtn, uMsg, wParam, lParam); 
//// }
////
/////*************************************************************************/
////
////void SetBtnProc(HWND hwnd) 
//// { 
//// /* Associate Exit Button and set PROC. */
//// BtnHWND[0] = GetDlgItem(hwnd,IDC_EXIT); 
//// SetWindowLong(GetDlgItem(hwnd, IDC_EXIT), GWL_WNDPROC, (LONG) BtnProc); 
//// /* Associate ClickMe button and set PROC. */
//// BtnHWND[1] = GetDlgItem(hwnd,IDC_BUTTON1); 
//// SetWindowLong(GetDlgItem(hwnd, IDC_BUTTON1), GWL_WNDPROC, (LONG) BtnProc); 
//// } 
////
/////*************************************************************************/
////
////void SetBtnInfo(HWND BtnHwnd) 
//// { 
//// /* Exit button. */
//// if(BtnHwnd == BtnHWND[0]) 
//// HoverBtnText = "Click here if you wish to exit from the Edge Module Demo Launcher."; 
//// /* ClickMe button. */
//// if(BtnHwnd == BtnHWND[1]) 
//// HoverBtnText ="Click Me && Find out what I do. \n Come on click ... click ... click..."; 
//// }
////
/////*************************************************************************/
////
////void OnClickMe() 
//// { 
//// MessageBox(NULL, "Click Me", "I have written CLICK on the console 10 times!", MB_OK); 
//// for(int i=0;i<10; i++) 
//// std::cout<<"CLICK"<<std::endl; 
//// }

#endif
