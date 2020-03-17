#include <iostream>
#include "Win32Gui.h"
#include "resource.h"
#include "afxwin.h"

using namespace POS;
using namespace POS::GUI;

HWND   _dlgHandle;
CComboBox *portcombo = NULL;

/******************************************************************************
 *
 ******************************************************************************/
LRESULT WINAPI WndProc(HWND hWnd, UINT Msg, WPARAM wParam, LPARAM lParam)
{
  if ( Msg==WM_DESTROY )
    PostQuitMessage(0);
  return DefWindowProc(hWnd, Msg, wParam, lParam);
}

/******************************************************************************
 *
 ******************************************************************************/
INT_PTR CALLBACK DialogProc(_In_  HWND hwndDlg,
                            _In_  UINT uMsg,
                            _In_  WPARAM wParam,
                            _In_  LPARAM lParam)
{
////  std::cout << "######## hwndDlg (" << hwndDlg << ") ######### UMsg ("
////            << uMsg << ") ######## wParam (" << wParam << ") ########## lParam ("
////            << lParam << ")\n";

  switch (uMsg)
  {
    case WM_CLOSE:
      if (MessageBox(NULL, TEXT("Really Quit?"), TEXT("Quit"),
                     MB_ICONQUESTION | MB_YESNO) == IDYES)
      {
        exit(0);
      }
      break;

  case WM_COMMAND:
    switch(LOWORD(wParam)) 
    {
////      case IDC_COMBO_PORT:
////        return(TRUE);
////        break;
    };
    break;
  };

  return(FALSE);
}

/******************************************************************************
 *
 ******************************************************************************/
Win32Gui::Win32Gui()
{
}

/******************************************************************************
 *
 ******************************************************************************/
Win32Gui::~Win32Gui()
{
}

/******************************************************************************
 *
 ******************************************************************************/
void Win32Gui::ShowTestDialog()
{
  HINSTANCE hInst = GetModuleHandle(0);
  WNDCLASS cls = { CS_HREDRAW|CS_VREDRAW, WndProc, 0, 0, hInst, LoadIcon(hInst,MAKEINTRESOURCE(IDI_APPLICATION)), 
                   LoadCursor(hInst,MAKEINTRESOURCE(IDC_ARROW)), GetSysColorBrush(COLOR_WINDOW),0,"Window" };
  RegisterClass( &cls );
  HWND window = CreateWindow("Window","Hello World",WS_OVERLAPPEDWINDOW|WS_VISIBLE,64,64,640,480,0,0,hInst,0);
}

/******************************************************************************
 *
 ******************************************************************************/
void Win32Gui::ShowTestDialog2()
{
  int nCmdShow = 0;

////  int retval = DialogBox(NULL, MAKEINTRESOURCE(IDD_DIALOG1),
////                         NULL, (DLGPROC)DialogProc);

  _dlgHandle = CreateDialog(NULL, MAKEINTRESOURCE(IDD_DIALOG1),
                            NULL, (DLGPROC)DialogProc);
  ShowWindow(_dlgHandle, SW_SHOW);


////  hDlg = CreateDialogParam(NULL, MAKEINTRESOURCE(IDD_DIALOG1), 0, DialogProc, 0);
////  ShowWindow(hDlg, nCmdShow);


  int gg = 0;

}

void Win32Gui::GetControls()
{
////      CComboBox *portcombo = (CComboBox*)CWnd::FromHandle((HWND)lParam);
////      portcombo = (CComboBox*)GetDlgItem(_dlgHandle, IDC_COMBO_PORT);

////  HWND hwndCombo = GetDlgItem(_dlgHandle, IDC_COMBO_PORT);
////  SendMessage(hwndCombo, CB_ADDSTRING, 0, (LPARAM)"COM1");
////  SendMessage(hwndCombo, CB_ADDSTRING, 0, (LPARAM)"COM2");
////  SendMessage(hwndCombo, CB_ADDSTRING, 0, (LPARAM)"COM3");
////  SendMessage(hwndCombo, CB_ADDSTRING, 0, (LPARAM)"COM4");
////  SendMessage(hwndCombo, CB_ADDSTRING, 0, (LPARAM)"COM5");
////  SendMessage(hwndCombo, CB_ADDSTRING, 0, (LPARAM)"COM6");
////  SendMessage(hwndCombo, CB_ADDSTRING, 0, (LPARAM)"COM7");
////  SendMessage(hwndCombo, CB_ADDSTRING, 0, (LPARAM)"COM8");
////  SendMessage(hwndCombo, CB_ADDSTRING, 0, (LPARAM)"COM9");
////  SendMessage(hwndCombo, CB_ADDSTRING, 0, (LPARAM)"COM10");

}
