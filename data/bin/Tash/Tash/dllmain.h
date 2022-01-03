// dllmain.h : Declaration of module class.

class CTashModule : public CAtlDllModuleT< CTashModule >
{
public :
	DECLARE_LIBID(LIBID_TashLib)
	DECLARE_REGISTRY_APPID_RESOURCEID(IDR_TASH, "{15CC4D83-F062-4D2F-AFFD-645527ED9C67}")
};

extern class CTashModule _AtlModule;
