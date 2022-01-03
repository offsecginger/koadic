

/* this ALWAYS GENERATED file contains the definitions for the interfaces */


 /* File created by MIDL compiler version 7.00.0500 */
/* at Mon Mar 25 00:42:22 2019
 */
/* Compiler settings for .\Tash.idl:
    Oicf, W1, Zp8, env=Win32 (32b run)
    protocol : dce , ms_ext, c_ext, robust
    error checks: stub_data 
    VC __declspec() decoration level: 
         __declspec(uuid()), __declspec(selectany), __declspec(novtable)
         DECLSPEC_UUID(), MIDL_INTERFACE()
*/
//@@MIDL_FILE_HEADING(  )

#pragma warning( disable: 4049 )  /* more than 64k source lines */


/* verify that the <rpcndr.h> version is high enough to compile this file*/
#ifndef __REQUIRED_RPCNDR_H_VERSION__
#define __REQUIRED_RPCNDR_H_VERSION__ 475
#endif

#include "rpc.h"
#include "rpcndr.h"

#ifndef __RPCNDR_H_VERSION__
#error this stub requires an updated version of <rpcndr.h>
#endif // __RPCNDR_H_VERSION__

#ifndef COM_NO_WINDOWS_H
#include "windows.h"
#include "ole2.h"
#endif /*COM_NO_WINDOWS_H*/

#ifndef __Tash_i_h__
#define __Tash_i_h__

#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

/* Forward Declarations */ 

#ifndef __ITashLoader_FWD_DEFINED__
#define __ITashLoader_FWD_DEFINED__
typedef interface ITashLoader ITashLoader;
#endif 	/* __ITashLoader_FWD_DEFINED__ */


#ifndef __TashLoader_FWD_DEFINED__
#define __TashLoader_FWD_DEFINED__

#ifdef __cplusplus
typedef class TashLoader TashLoader;
#else
typedef struct TashLoader TashLoader;
#endif /* __cplusplus */

#endif 	/* __TashLoader_FWD_DEFINED__ */


/* header files for imported files */
#include "oaidl.h"
#include "ocidl.h"

#ifdef __cplusplus
extern "C"{
#endif 


#ifndef __ITashLoader_INTERFACE_DEFINED__
#define __ITashLoader_INTERFACE_DEFINED__

/* interface ITashLoader */
/* [unique][helpstring][nonextensible][dual][uuid][object] */ 


EXTERN_C const IID IID_ITashLoader;

#if defined(__cplusplus) && !defined(CINTERFACE)
    
    MIDL_INTERFACE("5FF70415-14AE-403D-AADD-A797348C8967")
    ITashLoader : public IDispatch
    {
    public:
        virtual /* [helpstring][id] */ HRESULT STDMETHODCALLTYPE Load( 
            /* [in] */ BSTR sCode,
            /* [in] */ BSTR sParam,
            /* [in] */ ULONG dwOffset,
            /* [retval][out] */ ULONG *dwErr) = 0;
        
    };
    
#else 	/* C style interface */

    typedef struct ITashLoaderVtbl
    {
        BEGIN_INTERFACE
        
        HRESULT ( STDMETHODCALLTYPE *QueryInterface )( 
            ITashLoader * This,
            /* [in] */ REFIID riid,
            /* [iid_is][out] */ 
            __RPC__deref_out  void **ppvObject);
        
        ULONG ( STDMETHODCALLTYPE *AddRef )( 
            ITashLoader * This);
        
        ULONG ( STDMETHODCALLTYPE *Release )( 
            ITashLoader * This);
        
        HRESULT ( STDMETHODCALLTYPE *GetTypeInfoCount )( 
            ITashLoader * This,
            /* [out] */ UINT *pctinfo);
        
        HRESULT ( STDMETHODCALLTYPE *GetTypeInfo )( 
            ITashLoader * This,
            /* [in] */ UINT iTInfo,
            /* [in] */ LCID lcid,
            /* [out] */ ITypeInfo **ppTInfo);
        
        HRESULT ( STDMETHODCALLTYPE *GetIDsOfNames )( 
            ITashLoader * This,
            /* [in] */ REFIID riid,
            /* [size_is][in] */ LPOLESTR *rgszNames,
            /* [range][in] */ UINT cNames,
            /* [in] */ LCID lcid,
            /* [size_is][out] */ DISPID *rgDispId);
        
        /* [local] */ HRESULT ( STDMETHODCALLTYPE *Invoke )( 
            ITashLoader * This,
            /* [in] */ DISPID dispIdMember,
            /* [in] */ REFIID riid,
            /* [in] */ LCID lcid,
            /* [in] */ WORD wFlags,
            /* [out][in] */ DISPPARAMS *pDispParams,
            /* [out] */ VARIANT *pVarResult,
            /* [out] */ EXCEPINFO *pExcepInfo,
            /* [out] */ UINT *puArgErr);
        
        /* [helpstring][id] */ HRESULT ( STDMETHODCALLTYPE *Load )( 
            ITashLoader * This,
            /* [in] */ BSTR sCode,
            /* [in] */ BSTR sParam,
            /* [in] */ ULONG dwOffset,
            /* [retval][out] */ ULONG *dwErr);
        
        END_INTERFACE
    } ITashLoaderVtbl;

    interface ITashLoader
    {
        CONST_VTBL struct ITashLoaderVtbl *lpVtbl;
    };

    

#ifdef COBJMACROS


#define ITashLoader_QueryInterface(This,riid,ppvObject)	\
    ( (This)->lpVtbl -> QueryInterface(This,riid,ppvObject) ) 

#define ITashLoader_AddRef(This)	\
    ( (This)->lpVtbl -> AddRef(This) ) 

#define ITashLoader_Release(This)	\
    ( (This)->lpVtbl -> Release(This) ) 


#define ITashLoader_GetTypeInfoCount(This,pctinfo)	\
    ( (This)->lpVtbl -> GetTypeInfoCount(This,pctinfo) ) 

#define ITashLoader_GetTypeInfo(This,iTInfo,lcid,ppTInfo)	\
    ( (This)->lpVtbl -> GetTypeInfo(This,iTInfo,lcid,ppTInfo) ) 

#define ITashLoader_GetIDsOfNames(This,riid,rgszNames,cNames,lcid,rgDispId)	\
    ( (This)->lpVtbl -> GetIDsOfNames(This,riid,rgszNames,cNames,lcid,rgDispId) ) 

#define ITashLoader_Invoke(This,dispIdMember,riid,lcid,wFlags,pDispParams,pVarResult,pExcepInfo,puArgErr)	\
    ( (This)->lpVtbl -> Invoke(This,dispIdMember,riid,lcid,wFlags,pDispParams,pVarResult,pExcepInfo,puArgErr) ) 


#define ITashLoader_Load(This,sCode,sParam,dwOffset,dwErr)	\
    ( (This)->lpVtbl -> Load(This,sCode,sParam,dwOffset,dwErr) ) 

#endif /* COBJMACROS */


#endif 	/* C style interface */




#endif 	/* __ITashLoader_INTERFACE_DEFINED__ */



#ifndef __TashLib_LIBRARY_DEFINED__
#define __TashLib_LIBRARY_DEFINED__

/* library TashLib */
/* [helpstring][version][uuid] */ 


EXTERN_C const IID LIBID_TashLib;

EXTERN_C const CLSID CLSID_TashLoader;

#ifdef __cplusplus

class DECLSPEC_UUID("6AA5DEAB-5B77-4D09-BD8D-8EE26F2964AA")
TashLoader;
#endif
#endif /* __TashLib_LIBRARY_DEFINED__ */

/* Additional Prototypes for ALL interfaces */

unsigned long             __RPC_USER  BSTR_UserSize(     unsigned long *, unsigned long            , BSTR * ); 
unsigned char * __RPC_USER  BSTR_UserMarshal(  unsigned long *, unsigned char *, BSTR * ); 
unsigned char * __RPC_USER  BSTR_UserUnmarshal(unsigned long *, unsigned char *, BSTR * ); 
void                      __RPC_USER  BSTR_UserFree(     unsigned long *, BSTR * ); 

/* end of Additional Prototypes */

#ifdef __cplusplus
}
#endif

#endif


