// TashLoader.h : Declaration of the CTashLoader

#pragma once
#include "resource.h"       // main symbols

#include "Tash_i.h"


#if defined(_WIN32_WCE) && !defined(_CE_DCOM) && !defined(_CE_ALLOW_SINGLE_THREADED_OBJECTS_IN_MTA)
#error "Single-threaded COM objects are not properly supported on Windows CE platform, such as the Windows Mobile platforms that do not include full DCOM support. Define _CE_ALLOW_SINGLE_THREADED_OBJECTS_IN_MTA to force ATL to support creating single-thread COM object's and allow use of it's single-threaded COM object implementations. The threading model in your rgs file was set to 'Free' as that is the only threading model supported in non DCOM Windows CE platforms."
#endif



// CTashLoader

class ATL_NO_VTABLE CTashLoader :
	public CComObjectRootEx<CComMultiThreadModel>,
	public CComCoClass<CTashLoader, &CLSID_TashLoader>,
	public IDispatchImpl<ITashLoader, &IID_ITashLoader, &LIBID_TashLib, /*wMajor =*/ 1, /*wMinor =*/ 0>
{
public:
	CTashLoader()
	{
	}

DECLARE_REGISTRY_RESOURCEID(IDR_TASHLOADER)


BEGIN_COM_MAP(CTashLoader)
	COM_INTERFACE_ENTRY(ITashLoader)
	COM_INTERFACE_ENTRY(IDispatch)
END_COM_MAP()



	DECLARE_PROTECT_FINAL_CONSTRUCT()

	HRESULT FinalConstruct()
	{
		return S_OK;
	}

	void FinalRelease()
	{
	}

public:

	STDMETHOD(Load)(BSTR sCode, BSTR sParam, ULONG dwOffset, ULONG* dwErr);
};

OBJECT_ENTRY_AUTO(__uuidof(TashLoader), CTashLoader)
