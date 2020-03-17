#ifndef WIN_GUI
#define WIN_GUI

#include <wx/wxprec.h>
#ifndef WX_PRECOMP
    #include <wx/wx.h>
#endif

class WinGui: public wxApp
{
  public:
  virtual bool OnInit();
};

class WinFrame : public wxFrame
{
  public:
  enum
  {
    ID_Hello = 1
  };

  public:
  WinFrame(const wxString& title, const wxPoint& pos, const wxSize& size);

  private:
  void OnHello(wxCommandEvent& event);
  void OnExit(wxCommandEvent& event);
  void OnAbout(wxCommandEvent& event);
  wxDECLARE_EVENT_TABLE();
};

wxBEGIN_EVENT_TABLE(WinFrame, wxFrame)
    EVT_MENU(ID_Hello,   WinFrame::OnHello)
    EVT_MENU(wxID_EXIT,  WinFrame::OnExit)
    EVT_MENU(wxID_ABOUT, WinFrame::OnAbout)
wxEND_EVENT_TABLE()

wxIMPLEMENT_APP(WinGui);

#endif
