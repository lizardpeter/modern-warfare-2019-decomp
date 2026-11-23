typedef unsigned char   undefined;

typedef unsigned char    bool;
typedef unsigned char    byte;
typedef unsigned int    dword;
typedef unsigned long long    GUID;
typedef pointer32 ImageBaseOffset32;

typedef long long    longlong;
typedef unsigned long long    qword;
typedef unsigned char    uchar;
typedef unsigned int    uint;
typedef unsigned long    ulong;
typedef unsigned long long    ulonglong;
typedef unsigned char    undefined1;
typedef unsigned short    undefined2;
typedef unsigned int    undefined4;
typedef unsigned long long    undefined5;
typedef unsigned long long    undefined6;
typedef unsigned long long    undefined8;
typedef unsigned short    ushort;
typedef unsigned short    wchar16;
typedef unsigned int    wchar32;
typedef short    wchar_t;
typedef unsigned short    word;
typedef struct _s_HandlerType _s_HandlerType, *P_s_HandlerType;

struct _s_HandlerType {
    uint adjectives;
    ImageBaseOffset32 dispType;
    int dispCatchObj;
    ImageBaseOffset32 dispOfHandler;
    dword dispFrame;
};

typedef struct _s_IPToStateMapEntry _s_IPToStateMapEntry, *P_s_IPToStateMapEntry;

typedef struct _s_IPToStateMapEntry IPToStateMapEntry;

typedef int __ehstate_t;

struct _s_IPToStateMapEntry {
    ImageBaseOffset32 Ip;
    __ehstate_t state;
};

typedef union IMAGE_RESOURCE_DIRECTORY_ENTRY_DirectoryUnion IMAGE_RESOURCE_DIRECTORY_ENTRY_DirectoryUnion, *PIMAGE_RESOURCE_DIRECTORY_ENTRY_DirectoryUnion;

typedef struct IMAGE_RESOURCE_DIRECTORY_ENTRY_DirectoryStruct IMAGE_RESOURCE_DIRECTORY_ENTRY_DirectoryStruct, *PIMAGE_RESOURCE_DIRECTORY_ENTRY_DirectoryStruct;

struct IMAGE_RESOURCE_DIRECTORY_ENTRY_DirectoryStruct {
    dword OffsetToDirectory:31;
    dword DataIsDirectory:1;
};

union IMAGE_RESOURCE_DIRECTORY_ENTRY_DirectoryUnion {
    dword OffsetToData;
    struct IMAGE_RESOURCE_DIRECTORY_ENTRY_DirectoryStruct IMAGE_RESOURCE_DIRECTORY_ENTRY_DirectoryStruct;
};

typedef struct _s_FuncInfo _s_FuncInfo, *P_s_FuncInfo;

struct _s_FuncInfo {
    uint magicNumber_and_bbtFlags;
    __ehstate_t maxState;
    ImageBaseOffset32 dispUnwindMap;
    uint nTryBlocks;
    ImageBaseOffset32 dispTryBlockMap;
    uint nIPMapEntries;
    ImageBaseOffset32 dispIPToStateMap;
    int dispUnwindHelp;
    ImageBaseOffset32 dispESTypeList;
    int EHFlags;
};

typedef struct _s__RTTIBaseClassDescriptor _s__RTTIBaseClassDescriptor, *P_s__RTTIBaseClassDescriptor;

typedef struct _s__RTTIBaseClassDescriptor RTTIBaseClassDescriptor;

typedef RTTIBaseClassDescriptor *RTTIBaseClassDescriptor *32 __((image-base-relative));

typedef struct PMD PMD, *PPMD;

struct PMD {
    int mdisp;
    int pdisp;
    int vdisp;
};

struct _s__RTTIBaseClassDescriptor {
    ImageBaseOffset32 pTypeDescriptor; /* ref to TypeDescriptor (RTTI 0) for class */
    dword numContainedBases; /* count of extended classes in BaseClassArray (RTTI 2) */
    struct PMD where; /* member displacement structure */
    dword attributes; /* bit flags */
    ImageBaseOffset32 pClassHierarchyDescriptor; /* ref to ClassHierarchyDescriptor (RTTI 3) for class */
};

typedef struct _s__RTTICompleteObjectLocator _s__RTTICompleteObjectLocator, *P_s__RTTICompleteObjectLocator;

typedef struct _s__RTTICompleteObjectLocator RTTICompleteObjectLocator;

struct _s__RTTICompleteObjectLocator {
    dword signature;
    dword offset; /* offset of vbtable within class */
    dword cdOffset; /* constructor displacement offset */
    ImageBaseOffset32 pTypeDescriptor; /* ref to TypeDescriptor (RTTI 0) for class */
    ImageBaseOffset32 pClassDescriptor; /* ref to ClassHierarchyDescriptor (RTTI 3) */
};

typedef ulonglong __uint64;

typedef struct _s_HandlerType HandlerType;

typedef struct _s_TryBlockMapEntry _s_TryBlockMapEntry, *P_s_TryBlockMapEntry;

struct _s_TryBlockMapEntry {
    __ehstate_t tryLow;
    __ehstate_t tryHigh;
    __ehstate_t catchHigh;
    int nCatches;
    ImageBaseOffset32 dispHandlerArray;
};

typedef struct _s_TryBlockMapEntry TryBlockMapEntry;

typedef struct _com_error _com_error, *P_com_error;

struct _com_error { /* PlaceHolder Class Structure */
};

typedef RTTIBaseClassDescriptor *32 __((image-base-relative)) *RTTIBaseClassDescriptor *32 __((image-base-relative)) *32 __((image-base-relative));

typedef struct _s_UnwindMapEntry _s_UnwindMapEntry, *P_s_UnwindMapEntry;

typedef struct _s_UnwindMapEntry UnwindMapEntry;

struct _s_UnwindMapEntry {
    __ehstate_t toState;
    ImageBaseOffset32 action;
};

typedef struct CLIENT_ID CLIENT_ID, *PCLIENT_ID;

struct CLIENT_ID {
    void *UniqueProcess;
    void *UniqueThread;
};

typedef struct _s__RTTIClassHierarchyDescriptor _s__RTTIClassHierarchyDescriptor, *P_s__RTTIClassHierarchyDescriptor;

typedef struct _s__RTTIClassHierarchyDescriptor RTTIClassHierarchyDescriptor;

struct _s__RTTIClassHierarchyDescriptor {
    dword signature;
    dword attributes; /* bit flags */
    dword numBaseClasses; /* number of base classes (i.e. rtti1Count) */
    RTTIBaseClassDescriptor *32 __((image-base-relative)) *32 __((image-base-relative)) pBaseClassArray; /* ref to BaseClassArray (RTTI 2) */
};

typedef struct _s_FuncInfo FuncInfo;

typedef union _Fval _Fval, *P_Fval;

union _Fval {
    ushort _Sh[8];
    float _Val;
};

typedef struct _OVERLAPPED _OVERLAPPED, *P_OVERLAPPED;

typedef ulonglong ULONG_PTR;

typedef union _union_540 _union_540, *P_union_540;

typedef void *HANDLE;

typedef struct _struct_541 _struct_541, *P_struct_541;

typedef void *PVOID;

typedef ulong DWORD;

struct _struct_541 {
    DWORD Offset;
    DWORD OffsetHigh;
};

union _union_540 {
    struct _struct_541 s;
    PVOID Pointer;
};

struct _OVERLAPPED {
    ULONG_PTR Internal;
    ULONG_PTR InternalHigh;
    union _union_540 u;
    HANDLE hEvent;
};

typedef struct _SYSTEMTIME _SYSTEMTIME, *P_SYSTEMTIME;

typedef ushort WORD;

struct _SYSTEMTIME {
    WORD wYear;
    WORD wMonth;
    WORD wDayOfWeek;
    WORD wDay;
    WORD wHour;
    WORD wMinute;
    WORD wSecond;
    WORD wMilliseconds;
};

typedef struct _WIN32_FIND_DATAW _WIN32_FIND_DATAW, *P_WIN32_FIND_DATAW;

typedef struct _WIN32_FIND_DATAW *LPWIN32_FIND_DATAW;

typedef struct _FILETIME _FILETIME, *P_FILETIME;

typedef struct _FILETIME FILETIME;

typedef wchar_t WCHAR;

struct _FILETIME {
    DWORD dwLowDateTime;
    DWORD dwHighDateTime;
};

struct _WIN32_FIND_DATAW {
    DWORD dwFileAttributes;
    FILETIME ftCreationTime;
    FILETIME ftLastAccessTime;
    FILETIME ftLastWriteTime;
    DWORD nFileSizeHigh;
    DWORD nFileSizeLow;
    DWORD dwReserved0;
    DWORD dwReserved1;
    WCHAR cFileName[260];
    WCHAR cAlternateFileName[14];
};

typedef struct _struct_553 _struct_553, *P_struct_553;

struct _struct_553 {
    WORD wProcessorArchitecture;
    WORD wReserved;
};

typedef struct _WIN32_FIND_DATAA _WIN32_FIND_DATAA, *P_WIN32_FIND_DATAA;

typedef char CHAR;

struct _WIN32_FIND_DATAA {
    DWORD dwFileAttributes;
    FILETIME ftCreationTime;
    FILETIME ftLastAccessTime;
    FILETIME ftLastWriteTime;
    DWORD nFileSizeHigh;
    DWORD nFileSizeLow;
    DWORD dwReserved0;
    DWORD dwReserved1;
    CHAR cFileName[260];
    CHAR cAlternateFileName[14];
};

typedef void *LPVOID;

typedef void (*PFIBER_START_ROUTINE)(LPVOID);

typedef struct _SECURITY_ATTRIBUTES _SECURITY_ATTRIBUTES, *P_SECURITY_ATTRIBUTES;

typedef struct _SECURITY_ATTRIBUTES *LPSECURITY_ATTRIBUTES;

typedef int BOOL;

struct _SECURITY_ATTRIBUTES {
    DWORD nLength;
    LPVOID lpSecurityDescriptor;
    BOOL bInheritHandle;
};

typedef struct _STARTUPINFOA _STARTUPINFOA, *P_STARTUPINFOA;

typedef CHAR *LPSTR;

typedef uchar BYTE;

typedef BYTE *LPBYTE;

struct _STARTUPINFOA {
    DWORD cb;
    LPSTR lpReserved;
    LPSTR lpDesktop;
    LPSTR lpTitle;
    DWORD dwX;
    DWORD dwY;
    DWORD dwXSize;
    DWORD dwYSize;
    DWORD dwXCountChars;
    DWORD dwYCountChars;
    DWORD dwFillAttribute;
    DWORD dwFlags;
    WORD wShowWindow;
    WORD cbReserved2;
    LPBYTE lpReserved2;
    HANDLE hStdInput;
    HANDLE hStdOutput;
    HANDLE hStdError;
};

typedef enum _FINDEX_INFO_LEVELS {
    FindExInfoStandard=0,
    FindExInfoBasic=1,
    FindExInfoMaxInfoLevel=2
} _FINDEX_INFO_LEVELS;

typedef enum _FINDEX_INFO_LEVELS FINDEX_INFO_LEVELS;

typedef struct _TIME_ZONE_INFORMATION _TIME_ZONE_INFORMATION, *P_TIME_ZONE_INFORMATION;

typedef long LONG;

typedef struct _SYSTEMTIME SYSTEMTIME;

struct _TIME_ZONE_INFORMATION {
    LONG Bias;
    WCHAR StandardName[32];
    SYSTEMTIME StandardDate;
    LONG StandardBias;
    WCHAR DaylightName[32];
    SYSTEMTIME DaylightDate;
    LONG DaylightBias;
};

typedef struct _MEMORYSTATUS _MEMORYSTATUS, *P_MEMORYSTATUS;

typedef struct _MEMORYSTATUS *LPMEMORYSTATUS;

typedef ULONG_PTR SIZE_T;

struct _MEMORYSTATUS {
    DWORD dwLength;
    DWORD dwMemoryLoad;
    SIZE_T dwTotalPhys;
    SIZE_T dwAvailPhys;
    SIZE_T dwTotalPageFile;
    SIZE_T dwAvailPageFile;
    SIZE_T dwTotalVirtual;
    SIZE_T dwAvailVirtual;
};

typedef struct tagACTCTXW tagACTCTXW, *PtagACTCTXW;

typedef struct tagACTCTXW ACTCTXW;

typedef ulong ULONG;

typedef WCHAR *LPCWSTR;

typedef ushort USHORT;

typedef WORD LANGID;

typedef struct HINSTANCE__ HINSTANCE__, *PHINSTANCE__;

typedef struct HINSTANCE__ *HINSTANCE;

typedef HINSTANCE HMODULE;

struct HINSTANCE__ {
    int unused;
};

struct tagACTCTXW {
    ULONG cbSize;
    DWORD dwFlags;
    LPCWSTR lpSource;
    USHORT wProcessorArchitecture;
    LANGID wLangId;
    LPCWSTR lpAssemblyDirectory;
    LPCWSTR lpResourceName;
    LPCWSTR lpApplicationName;
    HMODULE hModule;
};

typedef struct _SYSTEM_INFO _SYSTEM_INFO, *P_SYSTEM_INFO;

typedef union _union_552 _union_552, *P_union_552;

typedef ULONG_PTR DWORD_PTR;

union _union_552 {
    DWORD dwOemId;
    struct _struct_553 s;
};

struct _SYSTEM_INFO {
    union _union_552 u;
    DWORD dwPageSize;
    LPVOID lpMinimumApplicationAddress;
    LPVOID lpMaximumApplicationAddress;
    DWORD_PTR dwActiveProcessorMask;
    DWORD dwNumberOfProcessors;
    DWORD dwProcessorType;
    DWORD dwAllocationGranularity;
    WORD wProcessorLevel;
    WORD wProcessorRevision;
};

typedef enum _FINDEX_SEARCH_OPS {
    FindExSearchNameMatch=0,
    FindExSearchLimitToDirectories=1,
    FindExSearchLimitToDevices=2,
    FindExSearchMaxSearchOp=3
} _FINDEX_SEARCH_OPS;

typedef DWORD (*PTHREAD_START_ROUTINE)(LPVOID);

typedef struct _SYSTEM_INFO *LPSYSTEM_INFO;

typedef struct _MEMORYSTATUSEX _MEMORYSTATUSEX, *P_MEMORYSTATUSEX;

typedef ulonglong ULONGLONG;

typedef ULONGLONG DWORDLONG;

struct _MEMORYSTATUSEX {
    DWORD dwLength;
    DWORD dwMemoryLoad;
    DWORDLONG ullTotalPhys;
    DWORDLONG ullAvailPhys;
    DWORDLONG ullTotalPageFile;
    DWORDLONG ullAvailPageFile;
    DWORDLONG ullTotalVirtual;
    DWORDLONG ullAvailVirtual;
    DWORDLONG ullAvailExtendedVirtual;
};

typedef struct _TIME_ZONE_INFORMATION TIME_ZONE_INFORMATION;

typedef struct _STARTUPINFOW _STARTUPINFOW, *P_STARTUPINFOW;

typedef struct _STARTUPINFOW *LPSTARTUPINFOW;

typedef WCHAR *LPWSTR;

struct _STARTUPINFOW {
    DWORD cb;
    LPWSTR lpReserved;
    LPWSTR lpDesktop;
    LPWSTR lpTitle;
    DWORD dwX;
    DWORD dwY;
    DWORD dwXSize;
    DWORD dwYSize;
    DWORD dwXCountChars;
    DWORD dwYCountChars;
    DWORD dwFillAttribute;
    DWORD dwFlags;
    WORD wShowWindow;
    WORD cbReserved2;
    LPBYTE lpReserved2;
    HANDLE hStdInput;
    HANDLE hStdOutput;
    HANDLE hStdError;
};

typedef struct _OVERLAPPED *LPOVERLAPPED;

typedef struct _STARTUPINFOA *LPSTARTUPINFOA;

typedef struct _RTL_CONDITION_VARIABLE _RTL_CONDITION_VARIABLE, *P_RTL_CONDITION_VARIABLE;

typedef struct _RTL_CONDITION_VARIABLE RTL_CONDITION_VARIABLE;

typedef RTL_CONDITION_VARIABLE *PCONDITION_VARIABLE;

struct _RTL_CONDITION_VARIABLE {
    PVOID Ptr;
};

typedef struct _RTL_SRWLOCK _RTL_SRWLOCK, *P_RTL_SRWLOCK;

typedef struct _RTL_SRWLOCK RTL_SRWLOCK;

typedef RTL_SRWLOCK *PSRWLOCK;

struct _RTL_SRWLOCK {
    PVOID Ptr;
};

typedef void (*LPOVERLAPPED_COMPLETION_ROUTINE)(DWORD, DWORD, LPOVERLAPPED);

typedef struct _SYSTEMTIME *LPSYSTEMTIME;

typedef struct _RTL_CRITICAL_SECTION _RTL_CRITICAL_SECTION, *P_RTL_CRITICAL_SECTION;

typedef struct _RTL_CRITICAL_SECTION *PRTL_CRITICAL_SECTION;

typedef PRTL_CRITICAL_SECTION PCRITICAL_SECTION;

typedef struct _RTL_CRITICAL_SECTION_DEBUG _RTL_CRITICAL_SECTION_DEBUG, *P_RTL_CRITICAL_SECTION_DEBUG;

typedef struct _RTL_CRITICAL_SECTION_DEBUG *PRTL_CRITICAL_SECTION_DEBUG;

typedef struct _LIST_ENTRY _LIST_ENTRY, *P_LIST_ENTRY;

typedef struct _LIST_ENTRY LIST_ENTRY;

struct _RTL_CRITICAL_SECTION {
    PRTL_CRITICAL_SECTION_DEBUG DebugInfo;
    LONG LockCount;
    LONG RecursionCount;
    HANDLE OwningThread;
    HANDLE LockSemaphore;
    ULONG_PTR SpinCount;
};

struct _LIST_ENTRY {
    struct _LIST_ENTRY *Flink;
    struct _LIST_ENTRY *Blink;
};

struct _RTL_CRITICAL_SECTION_DEBUG {
    WORD Type;
    WORD CreatorBackTraceIndex;
    struct _RTL_CRITICAL_SECTION *CriticalSection;
    LIST_ENTRY ProcessLocksList;
    DWORD EntryCount;
    DWORD ContentionCount;
    DWORD Flags;
    WORD CreatorBackTraceIndexHigh;
    WORD SpareWORD;
};

typedef ACTCTXW *PCACTCTXW;

typedef struct _BY_HANDLE_FILE_INFORMATION _BY_HANDLE_FILE_INFORMATION, *P_BY_HANDLE_FILE_INFORMATION;

struct _BY_HANDLE_FILE_INFORMATION {
    DWORD dwFileAttributes;
    FILETIME ftCreationTime;
    FILETIME ftLastAccessTime;
    FILETIME ftLastWriteTime;
    DWORD dwVolumeSerialNumber;
    DWORD nFileSizeHigh;
    DWORD nFileSizeLow;
    DWORD nNumberOfLinks;
    DWORD nFileIndexHigh;
    DWORD nFileIndexLow;
};

typedef enum _GET_FILEEX_INFO_LEVELS {
    GetFileExInfoStandard=0,
    GetFileExMaxInfoLevel=1
} _GET_FILEEX_INFO_LEVELS;

typedef enum _GET_FILEEX_INFO_LEVELS GET_FILEEX_INFO_LEVELS;

typedef struct _PROCESS_INFORMATION _PROCESS_INFORMATION, *P_PROCESS_INFORMATION;

typedef struct _PROCESS_INFORMATION *LPPROCESS_INFORMATION;

struct _PROCESS_INFORMATION {
    HANDLE hProcess;
    HANDLE hThread;
    DWORD dwProcessId;
    DWORD dwThreadId;
};

typedef struct _CONTEXT _CONTEXT, *P_CONTEXT;

typedef struct _CONTEXT *PCONTEXT;

typedef PCONTEXT LPCONTEXT;

typedef ulonglong DWORD64;

typedef union _union_54 _union_54, *P_union_54;

typedef struct _M128A _M128A, *P_M128A;

typedef struct _M128A M128A;

typedef struct _XSAVE_FORMAT _XSAVE_FORMAT, *P_XSAVE_FORMAT;

typedef struct _XSAVE_FORMAT XSAVE_FORMAT;

typedef XSAVE_FORMAT XMM_SAVE_AREA32;

typedef struct _struct_55 _struct_55, *P_struct_55;

typedef longlong LONGLONG;

struct _M128A {
    ULONGLONG Low;
    LONGLONG High;
};

struct _XSAVE_FORMAT {
    WORD ControlWord;
    WORD StatusWord;
    BYTE TagWord;
    BYTE Reserved1;
    WORD ErrorOpcode;
    DWORD ErrorOffset;
    WORD ErrorSelector;
    WORD Reserved2;
    DWORD DataOffset;
    WORD DataSelector;
    WORD Reserved3;
    DWORD MxCsr;
    DWORD MxCsr_Mask;
    M128A FloatRegisters[8];
    M128A XmmRegisters[16];
    BYTE Reserved4[96];
};

struct _struct_55 {
    M128A Header[2];
    M128A Legacy[8];
    M128A Xmm0;
    M128A Xmm1;
    M128A Xmm2;
    M128A Xmm3;
    M128A Xmm4;
    M128A Xmm5;
    M128A Xmm6;
    M128A Xmm7;
    M128A Xmm8;
    M128A Xmm9;
    M128A Xmm10;
    M128A Xmm11;
    M128A Xmm12;
    M128A Xmm13;
    M128A Xmm14;
    M128A Xmm15;
};

union _union_54 {
    XMM_SAVE_AREA32 FltSave;
    struct _struct_55 s;
};

struct _CONTEXT {
    DWORD64 P1Home;
    DWORD64 P2Home;
    DWORD64 P3Home;
    DWORD64 P4Home;
    DWORD64 P5Home;
    DWORD64 P6Home;
    DWORD ContextFlags;
    DWORD MxCsr;
    WORD SegCs;
    WORD SegDs;
    WORD SegEs;
    WORD SegFs;
    WORD SegGs;
    WORD SegSs;
    DWORD EFlags;
    DWORD64 Dr0;
    DWORD64 Dr1;
    DWORD64 Dr2;
    DWORD64 Dr3;
    DWORD64 Dr6;
    DWORD64 Dr7;
    DWORD64 Rax;
    DWORD64 Rcx;
    DWORD64 Rdx;
    DWORD64 Rbx;
    DWORD64 Rsp;
    DWORD64 Rbp;
    DWORD64 Rsi;
    DWORD64 Rdi;
    DWORD64 R8;
    DWORD64 R9;
    DWORD64 R10;
    DWORD64 R11;
    DWORD64 R12;
    DWORD64 R13;
    DWORD64 R14;
    DWORD64 R15;
    DWORD64 Rip;
    union _union_54 u;
    M128A VectorRegister[26];
    DWORD64 VectorControl;
    DWORD64 DebugControl;
    DWORD64 LastBranchToRip;
    DWORD64 LastBranchFromRip;
    DWORD64 LastExceptionToRip;
    DWORD64 LastExceptionFromRip;
};

typedef struct _EXCEPTION_POINTERS _EXCEPTION_POINTERS, *P_EXCEPTION_POINTERS;

typedef LONG (*PTOP_LEVEL_EXCEPTION_FILTER)(struct _EXCEPTION_POINTERS *);

typedef PTOP_LEVEL_EXCEPTION_FILTER LPTOP_LEVEL_EXCEPTION_FILTER;

typedef struct _EXCEPTION_RECORD _EXCEPTION_RECORD, *P_EXCEPTION_RECORD;

typedef struct _EXCEPTION_RECORD EXCEPTION_RECORD;

typedef EXCEPTION_RECORD *PEXCEPTION_RECORD;

struct _EXCEPTION_RECORD {
    DWORD ExceptionCode;
    DWORD ExceptionFlags;
    struct _EXCEPTION_RECORD *ExceptionRecord;
    PVOID ExceptionAddress;
    DWORD NumberParameters;
    ULONG_PTR ExceptionInformation[15];
};

struct _EXCEPTION_POINTERS {
    PEXCEPTION_RECORD ExceptionRecord;
    PCONTEXT ContextRecord;
};

typedef struct _TIME_ZONE_INFORMATION *LPTIME_ZONE_INFORMATION;

typedef PFIBER_START_ROUTINE LPFIBER_START_ROUTINE;

typedef PTHREAD_START_ROUTINE LPTHREAD_START_ROUTINE;

typedef struct _MEMORYSTATUSEX *LPMEMORYSTATUSEX;

typedef enum _FINDEX_SEARCH_OPS FINDEX_SEARCH_OPS;

typedef struct _WIN32_FIND_DATAA *LPWIN32_FIND_DATAA;

typedef struct _BY_HANDLE_FILE_INFORMATION *LPBY_HANDLE_FILE_INFORMATION;

typedef PRTL_CRITICAL_SECTION LPCRITICAL_SECTION;


/* WARNING! conflicting data type names: /wtypes.h/ULONG - /WinDef.h/ULONG */

typedef WCHAR OLECHAR;

typedef struct _Ctypevec _Ctypevec, *P_Ctypevec;

struct _Ctypevec {
    uint _Page;
    short *_Table;
    int _Delfl;
    wchar_t *_LocaleName;
};

typedef struct _iobuf _iobuf, *P_iobuf;

struct _iobuf {
    char *_ptr;
    int _cnt;
    char *_base;
    int _flag;
    int _file;
    int _charbuf;
    int _bufsiz;
    char *_tmpfname;
};

typedef struct _iobuf FILE;

typedef int PMFN;

typedef struct _s_ThrowInfo _s_ThrowInfo, *P_s_ThrowInfo;

typedef struct _s_ThrowInfo ThrowInfo;

struct _s_ThrowInfo {
    uint attributes;
    PMFN pmfnUnwind;
    int pForwardCompat;
    int pCatchableTypeArray;
};

typedef struct TypeDescriptor TypeDescriptor, *PTypeDescriptor;

struct TypeDescriptor {
    void *pVFTable;
    void *spare;
    char name[0];
};

typedef char *va_list;

typedef ulonglong uintptr_t;

typedef struct tagMONITORINFO tagMONITORINFO, *PtagMONITORINFO;

typedef struct tagMONITORINFO *LPMONITORINFO;

typedef struct tagRECT tagRECT, *PtagRECT;

typedef struct tagRECT RECT;

struct tagRECT {
    LONG left;
    LONG top;
    LONG right;
    LONG bottom;
};

struct tagMONITORINFO {
    DWORD cbSize;
    RECT rcMonitor;
    RECT rcWork;
    DWORD dwFlags;
};

typedef struct tagMSG tagMSG, *PtagMSG;

typedef struct tagMSG *LPMSG;

typedef struct HWND__ HWND__, *PHWND__;

typedef struct HWND__ *HWND;

typedef uint UINT;

typedef ulonglong UINT_PTR;

typedef UINT_PTR WPARAM;

typedef longlong LONG_PTR;

typedef LONG_PTR LPARAM;

typedef struct tagPOINT tagPOINT, *PtagPOINT;

typedef struct tagPOINT POINT;

struct tagPOINT {
    LONG x;
    LONG y;
};

struct tagMSG {
    HWND hwnd;
    UINT message;
    WPARAM wParam;
    LPARAM lParam;
    DWORD time;
    POINT pt;
};

struct HWND__ {
    int unused;
};

typedef struct tagRAWINPUTHEADER tagRAWINPUTHEADER, *PtagRAWINPUTHEADER;

struct tagRAWINPUTHEADER {
    DWORD dwType;
    DWORD dwSize;
    HANDLE hDevice;
    WPARAM wParam;
};

typedef struct tagRAWINPUTDEVICE tagRAWINPUTDEVICE, *PtagRAWINPUTDEVICE;

typedef struct tagRAWINPUTDEVICE RAWINPUTDEVICE;

struct tagRAWINPUTDEVICE {
    USHORT usUsagePage;
    USHORT usUsage;
    DWORD dwFlags;
    HWND hwndTarget;
};

typedef struct tagRAWINPUT tagRAWINPUT, *PtagRAWINPUT;

typedef struct tagRAWINPUTHEADER RAWINPUTHEADER;

typedef union _union_950 _union_950, *P_union_950;

typedef struct tagRAWMOUSE tagRAWMOUSE, *PtagRAWMOUSE;

typedef struct tagRAWMOUSE RAWMOUSE;

typedef struct tagRAWKEYBOARD tagRAWKEYBOARD, *PtagRAWKEYBOARD;

typedef struct tagRAWKEYBOARD RAWKEYBOARD;

typedef struct tagRAWHID tagRAWHID, *PtagRAWHID;

typedef struct tagRAWHID RAWHID;

typedef union _union_945 _union_945, *P_union_945;

typedef struct _struct_946 _struct_946, *P_struct_946;

struct _struct_946 {
    USHORT usButtonFlags;
    USHORT usButtonData;
};

union _union_945 {
    ULONG ulButtons;
    struct _struct_946 field1;
};

struct tagRAWHID {
    DWORD dwSizeHid;
    DWORD dwCount;
    BYTE bRawData[1];
};

struct tagRAWKEYBOARD {
    USHORT MakeCode;
    USHORT Flags;
    USHORT Reserved;
    USHORT VKey;
    UINT Message;
    ULONG ExtraInformation;
};

struct tagRAWMOUSE {
    USHORT usFlags;
    union _union_945 field1_0x4;
    ULONG ulRawButtons;
    LONG lLastX;
    LONG lLastY;
    ULONG ulExtraInformation;
};

union _union_950 {
    RAWMOUSE mouse;
    RAWKEYBOARD keyboard;
    RAWHID hid;
};

struct tagRAWINPUT {
    RAWINPUTHEADER header;
    union _union_950 data;
};

typedef LONG_PTR LRESULT;

typedef LRESULT (*HOOKPROC)(int, WPARAM, LPARAM);

typedef struct tagPAINTSTRUCT tagPAINTSTRUCT, *PtagPAINTSTRUCT;

typedef struct tagPAINTSTRUCT *LPPAINTSTRUCT;

typedef struct HDC__ HDC__, *PHDC__;

typedef struct HDC__ *HDC;

struct HDC__ {
    int unused;
};

struct tagPAINTSTRUCT {
    HDC hdc;
    BOOL fErase;
    RECT rcPaint;
    BOOL fRestore;
    BOOL fIncUpdate;
    BYTE rgbReserved[32];
};

typedef LRESULT (*WNDPROC)(HWND, UINT, WPARAM, LPARAM);

typedef struct tagWNDCLASSEXW tagWNDCLASSEXW, *PtagWNDCLASSEXW;

typedef struct tagWNDCLASSEXW WNDCLASSEXW;

typedef struct HICON__ HICON__, *PHICON__;

typedef struct HICON__ *HICON;

typedef HICON HCURSOR;

typedef struct HBRUSH__ HBRUSH__, *PHBRUSH__;

typedef struct HBRUSH__ *HBRUSH;

struct HBRUSH__ {
    int unused;
};

struct HICON__ {
    int unused;
};

struct tagWNDCLASSEXW {
    UINT cbSize;
    UINT style;
    WNDPROC lpfnWndProc;
    int cbClsExtra;
    int cbWndExtra;
    HINSTANCE hInstance;
    HICON hIcon;
    HCURSOR hCursor;
    HBRUSH hbrBackground;
    LPCWSTR lpszMenuName;
    LPCWSTR lpszClassName;
    HICON hIconSm;
};

typedef struct tagPAINTSTRUCT PAINTSTRUCT;

typedef struct tagWNDCLASSW tagWNDCLASSW, *PtagWNDCLASSW;

typedef struct tagWNDCLASSW WNDCLASSW;

struct tagWNDCLASSW {
    UINT style;
    WNDPROC lpfnWndProc;
    int cbClsExtra;
    int cbWndExtra;
    HINSTANCE hInstance;
    HICON hIcon;
    HCURSOR hCursor;
    HBRUSH hbrBackground;
    LPCWSTR lpszMenuName;
    LPCWSTR lpszClassName;
};

typedef BOOL (*WNDENUMPROC)(HWND, LPARAM);

typedef void (*TIMERPROC)(HWND, UINT, UINT_PTR, DWORD);

typedef struct tagWINDOWPLACEMENT tagWINDOWPLACEMENT, *PtagWINDOWPLACEMENT;

typedef struct tagWINDOWPLACEMENT WINDOWPLACEMENT;

struct tagWINDOWPLACEMENT {
    UINT length;
    UINT flags;
    UINT showCmd;
    POINT ptMinPosition;
    POINT ptMaxPosition;
    RECT rcNormalPosition;
};

typedef struct tagMSG MSG;

typedef RAWINPUTDEVICE *PCRAWINPUTDEVICE;

typedef struct tagRAWINPUT *PRAWINPUT;

typedef struct HMONITOR__ HMONITOR__, *PHMONITOR__;

typedef struct HMONITOR__ *HMONITOR;

typedef struct tagRECT *LPRECT;

typedef BOOL (*MONITORENUMPROC)(HMONITOR, HDC, LPRECT, LPARAM);

struct HMONITOR__ {
    int unused;
};

typedef struct exception exception, *Pexception;

struct exception { /* PlaceHolder Class Structure */
};

typedef struct ctype<char> ctype<char>, *Pctype<char>;

struct ctype<char> { /* PlaceHolder Class Structure */
};

typedef struct _Locimp _Locimp, *P_Locimp;

struct _Locimp { /* PlaceHolder Class Structure */
};

typedef struct IMAGE_DOS_HEADER IMAGE_DOS_HEADER, *PIMAGE_DOS_HEADER;

struct IMAGE_DOS_HEADER {
    char e_magic[2]; /* Magic number */
    word e_cblp; /* Bytes of last page */
    word e_cp; /* Pages in file */
    word e_crlc; /* Relocations */
    word e_cparhdr; /* Size of header in paragraphs */
    word e_minalloc; /* Minimum extra paragraphs needed */
    word e_maxalloc; /* Maximum extra paragraphs needed */
    word e_ss; /* Initial (relative) SS value */
    word e_sp; /* Initial SP value */
    word e_csum; /* Checksum */
    word e_ip; /* Initial IP value */
    word e_cs; /* Initial (relative) CS value */
    word e_lfarlc; /* File address of relocation table */
    word e_ovno; /* Overlay number */
    word e_res[4][4]; /* Reserved words */
    word e_oemid; /* OEM identifier (for e_oeminfo) */
    word e_oeminfo; /* OEM information; e_oemid specific */
    word e_res2[10][10]; /* Reserved words */
    dword e_lfanew; /* File address of new exe header */
    byte e_program[64]; /* Actual DOS program */
};

typedef ULONG_PTR *PDWORD_PTR;

typedef ulonglong *PDWORD64;

typedef uint UINT32;

typedef longlong INT_PTR;

typedef ulonglong UINT64;

typedef UINT MMVERSION;

typedef struct tMIXERCONTROLDETAILS tMIXERCONTROLDETAILS, *PtMIXERCONTROLDETAILS;

typedef union _union_1121 _union_1121, *P_union_1121;

union _union_1121 {
    HWND hwndOwner;
    DWORD cMultipleItems;
};

struct tMIXERCONTROLDETAILS {
    DWORD cbStruct;
    DWORD dwControlID;
    DWORD cChannels;
    union _union_1121 u;
    DWORD cbDetails;
    LPVOID paDetails;
};

typedef struct timecaps_tag timecaps_tag, *Ptimecaps_tag;

struct timecaps_tag {
    UINT wPeriodMin;
    UINT wPeriodMax;
};

typedef struct _struct_1105 _struct_1105, *P_struct_1105;

struct _struct_1105 {
    DWORD dwType;
    DWORD dwDeviceID;
    WORD wMid;
    WORD wPid;
    MMVERSION vDriverVersion;
    WCHAR szPname[32];
};

typedef struct tagMIXERLINEW tagMIXERLINEW, *PtagMIXERLINEW;

typedef struct tagMIXERLINEW *LPMIXERLINEW;

struct tagMIXERLINEW {
    DWORD cbStruct;
    DWORD dwDestination;
    DWORD dwSource;
    DWORD dwLineID;
    DWORD fdwLine;
    DWORD_PTR dwUser;
    DWORD dwComponentType;
    DWORD cChannels;
    DWORD cConnections;
    DWORD cControls;
    WCHAR szShortName[16];
    WCHAR szName[64];
    struct _struct_1105 Target;
};

typedef struct tagWAVEINCAPSW tagWAVEINCAPSW, *PtagWAVEINCAPSW;

struct tagWAVEINCAPSW {
    WORD wMid;
    WORD wPid;
    MMVERSION vDriverVersion;
    WCHAR szPname[32];
    DWORD dwFormats;
    WORD wChannels;
    WORD wReserved1;
};

typedef struct tagMIXERLINECONTROLSW tagMIXERLINECONTROLSW, *PtagMIXERLINECONTROLSW;

typedef union _union_1119 _union_1119, *P_union_1119;

typedef struct tagMIXERCONTROLW tagMIXERCONTROLW, *PtagMIXERCONTROLW;

typedef struct tagMIXERCONTROLW *LPMIXERCONTROLW;

typedef union _union_1112 _union_1112, *P_union_1112;

typedef union _union_1115 _union_1115, *P_union_1115;

typedef struct _struct_1113 _struct_1113, *P_struct_1113;

typedef struct _struct_1114 _struct_1114, *P_struct_1114;

union _union_1115 {
    DWORD cSteps;
    DWORD cbCustomData;
    DWORD dwReserved[6];
};

struct _struct_1113 {
    LONG lMinimum;
    LONG lMaximum;
};

struct _struct_1114 {
    DWORD dwMinimum;
    DWORD dwMaximum;
};

union _union_1112 {
    struct _struct_1113 s;
    struct _struct_1114 s2;
    DWORD dwReserved[6];
};

struct tagMIXERCONTROLW {
    DWORD cbStruct;
    DWORD dwControlID;
    DWORD dwControlType;
    DWORD fdwControl;
    DWORD cMultipleItems;
    WCHAR szShortName[16];
    WCHAR szName[64];
    union _union_1112 Bounds;
    union _union_1115 Metrics;
};

union _union_1119 {
    DWORD dwControlID;
    DWORD dwControlType;
};

struct tagMIXERLINECONTROLSW {
    DWORD cbStruct;
    DWORD dwLineID;
    union _union_1119 u;
    DWORD cControls;
    DWORD cbmxctrl;
    LPMIXERCONTROLW pamxctrl;
};

typedef struct tagMIXERLINECONTROLSW *LPMIXERLINECONTROLSW;

typedef struct HMIXEROBJ__ HMIXEROBJ__, *PHMIXEROBJ__;

typedef struct HMIXEROBJ__ *HMIXEROBJ;

struct HMIXEROBJ__ {
    int unused;
};

typedef struct timecaps_tag *LPTIMECAPS;

typedef struct tagWAVEOUTCAPSW tagWAVEOUTCAPSW, *PtagWAVEOUTCAPSW;

typedef struct tagWAVEOUTCAPSW *LPWAVEOUTCAPSW;

struct tagWAVEOUTCAPSW {
    WORD wMid;
    WORD wPid;
    MMVERSION vDriverVersion;
    WCHAR szPname[32];
    DWORD dwFormats;
    WORD wChannels;
    WORD wReserved1;
    DWORD dwSupport;
};

typedef UINT MMRESULT;

typedef struct tMIXERCONTROLDETAILS *LPMIXERCONTROLDETAILS;

typedef struct tagWAVEINCAPSW *LPWAVEINCAPSW;

typedef struct REFMINIPDB2 REFMINIPDB2, *PREFMINIPDB2;

struct REFMINIPDB2 { /* PlaceHolder Structure */
};

typedef struct <lambda_6da5eaf298b4749753c721cc8c61e051> <lambda_6da5eaf298b4749753c721cc8c61e051>, *P<lambda_6da5eaf298b4749753c721cc8c61e051>;

struct <lambda_6da5eaf298b4749753c721cc8c61e051> { /* PlaceHolder Structure */
};

typedef struct MemBlock MemBlock, *PMemBlock;

struct MemBlock { /* PlaceHolder Structure */
};

typedef struct <lambda_f7f22ab5edc0698d5f6905b0d3f44752> <lambda_f7f22ab5edc0698d5f6905b0d3f44752>, *P<lambda_f7f22ab5edc0698d5f6905b0d3f44752>;

struct <lambda_f7f22ab5edc0698d5f6905b0d3f44752> { /* PlaceHolder Structure */
};

typedef struct <lambda_3e16ef9562a7dcce91392c22ab16ea36> <lambda_3e16ef9562a7dcce91392c22ab16ea36>, *P<lambda_3e16ef9562a7dcce91392c22ab16ea36>;

struct <lambda_3e16ef9562a7dcce91392c22ab16ea36> { /* PlaceHolder Structure */
};

typedef struct <lambda_f3caf1ecae5fe01a9a1a6239afa44510> <lambda_f3caf1ecae5fe01a9a1a6239afa44510>, *P<lambda_f3caf1ecae5fe01a9a1a6239afa44510>;

struct <lambda_f3caf1ecae5fe01a9a1a6239afa44510> { /* PlaceHolder Structure */
};

typedef struct __acrt_thread_parameter __acrt_thread_parameter, *P__acrt_thread_parameter;

struct __acrt_thread_parameter { /* PlaceHolder Structure */
};

typedef struct <lambda_1d892b297fdedeee07ed8124eeb2f2fa> <lambda_1d892b297fdedeee07ed8124eeb2f2fa>, *P<lambda_1d892b297fdedeee07ed8124eeb2f2fa>;

struct <lambda_1d892b297fdedeee07ed8124eeb2f2fa> { /* PlaceHolder Structure */
};

typedef struct _stat64i32 _stat64i32, *P_stat64i32;

struct _stat64i32 { /* PlaceHolder Structure */
};

typedef struct <lambda_7777bce6b2f8c936911f934f8298dc43> <lambda_7777bce6b2f8c936911f934f8298dc43>, *P<lambda_7777bce6b2f8c936911f934f8298dc43>;

struct <lambda_7777bce6b2f8c936911f934f8298dc43> { /* PlaceHolder Structure */
};

typedef struct <lambda_a37b2b86f63e897a80ea819b0eb08c01> <lambda_a37b2b86f63e897a80ea819b0eb08c01>, *P<lambda_a37b2b86f63e897a80ea819b0eb08c01>;

struct <lambda_a37b2b86f63e897a80ea819b0eb08c01> { /* PlaceHolder Structure */
};

typedef struct <lambda_2358e3775559c9db80273638284d5e45> <lambda_2358e3775559c9db80273638284d5e45>, *P<lambda_2358e3775559c9db80273638284d5e45>;

struct <lambda_2358e3775559c9db80273638284d5e45> { /* PlaceHolder Structure */
};

typedef struct _Mbstatet _Mbstatet, *P_Mbstatet;

struct _Mbstatet { /* PlaceHolder Structure */
};

typedef struct __crt_locale_data __crt_locale_data, *P__crt_locale_data;

struct __crt_locale_data { /* PlaceHolder Structure */
};

typedef struct _Cnd_internal_imp_t _Cnd_internal_imp_t, *P_Cnd_internal_imp_t;

struct _Cnd_internal_imp_t { /* PlaceHolder Structure */
};

typedef struct <lambda_886d6c58226a84441f68b9f2b8217b83> <lambda_886d6c58226a84441f68b9f2b8217b83>, *P<lambda_886d6c58226a84441f68b9f2b8217b83>;

struct <lambda_886d6c58226a84441f68b9f2b8217b83> { /* PlaceHolder Structure */
};

typedef struct <lambda_c8e61daa512c69656564d9dbd35486e8> <lambda_c8e61daa512c69656564d9dbd35486e8>, *P<lambda_c8e61daa512c69656564d9dbd35486e8>;

struct <lambda_c8e61daa512c69656564d9dbd35486e8> { /* PlaceHolder Structure */
};

typedef struct <lambda_572fbb9fa0ab338edf41edfd4b5fcc8d> <lambda_572fbb9fa0ab338edf41edfd4b5fcc8d>, *P<lambda_572fbb9fa0ab338edf41edfd4b5fcc8d>;

struct <lambda_572fbb9fa0ab338edf41edfd4b5fcc8d> { /* PlaceHolder Structure */
};

typedef struct <lambda_a6f7d7db0129f75315ebf26d50c089f1> <lambda_a6f7d7db0129f75315ebf26d50c089f1>, *P<lambda_a6f7d7db0129f75315ebf26d50c089f1>;

struct <lambda_a6f7d7db0129f75315ebf26d50c089f1> { /* PlaceHolder Structure */
};

typedef struct <lambda_c640b76c0755ae85b317b35c67c61e6b> <lambda_c640b76c0755ae85b317b35c67c61e6b>, *P<lambda_c640b76c0755ae85b317b35c67c61e6b>;

struct <lambda_c640b76c0755ae85b317b35c67c61e6b> { /* PlaceHolder Structure */
};

typedef struct <lambda_d80eeec6fff315bfe5c115232f3240e3> <lambda_d80eeec6fff315bfe5c115232f3240e3>, *P<lambda_d80eeec6fff315bfe5c115232f3240e3>;

struct <lambda_d80eeec6fff315bfe5c115232f3240e3> { /* PlaceHolder Structure */
};

typedef struct <lambda_f03950bc5685219e0bcd2087efbe011e> <lambda_f03950bc5685219e0bcd2087efbe011e>, *P<lambda_f03950bc5685219e0bcd2087efbe011e>;

struct <lambda_f03950bc5685219e0bcd2087efbe011e> { /* PlaceHolder Structure */
};

typedef struct <lambda_c5860995281e5c4ce005b3de8f5874ee> <lambda_c5860995281e5c4ce005b3de8f5874ee>, *P<lambda_c5860995281e5c4ce005b3de8f5874ee>;

struct <lambda_c5860995281e5c4ce005b3de8f5874ee> { /* PlaceHolder Structure */
};

typedef struct <lambda_842d9ff0dc9ef11c61343bbaebe7f885> <lambda_842d9ff0dc9ef11c61343bbaebe7f885>, *P<lambda_842d9ff0dc9ef11c61343bbaebe7f885>;

struct <lambda_842d9ff0dc9ef11c61343bbaebe7f885> { /* PlaceHolder Structure */
};

typedef struct <lambda_b579ea784fd840951dfbcbdaebf709fd> <lambda_b579ea784fd840951dfbcbdaebf709fd>, *P<lambda_b579ea784fd840951dfbcbdaebf709fd>;

struct <lambda_b579ea784fd840951dfbcbdaebf709fd> { /* PlaceHolder Structure */
};

typedef enum _crt_exit_cleanup_mode {
} _crt_exit_cleanup_mode;

typedef struct <lambda_2a444430fde8c29194d880d93eed5e8f> <lambda_2a444430fde8c29194d880d93eed5e8f>, *P<lambda_2a444430fde8c29194d880d93eed5e8f>;

struct <lambda_2a444430fde8c29194d880d93eed5e8f> { /* PlaceHolder Structure */
};

typedef struct __crt_seh_guarded_call<void> __crt_seh_guarded_call<void>, *P__crt_seh_guarded_call<void>;

struct __crt_seh_guarded_call<void> { /* PlaceHolder Structure */
};

typedef struct __crt_win32_buffer<char,__crt_win32_buffer_no_resizing> __crt_win32_buffer<char,__crt_win32_buffer_no_resizing>, *P__crt_win32_buffer<char,__crt_win32_buffer_no_resizing>;

struct __crt_win32_buffer<char,__crt_win32_buffer_no_resizing> { /* PlaceHolder Structure */
};

typedef struct <lambda_e638437c4db75b75056fab6aaf7e4f15> <lambda_e638437c4db75b75056fab6aaf7e4f15>, *P<lambda_e638437c4db75b75056fab6aaf7e4f15>;

struct <lambda_e638437c4db75b75056fab6aaf7e4f15> { /* PlaceHolder Structure */
};

typedef struct <lambda_2ca749746f96040ea1ff4296b14379df> <lambda_2ca749746f96040ea1ff4296b14379df>, *P<lambda_2ca749746f96040ea1ff4296b14379df>;

struct <lambda_2ca749746f96040ea1ff4296b14379df> { /* PlaceHolder Structure */
};

typedef struct <lambda_3883c3dff614d5e0c5f61bb1ac94921c> <lambda_3883c3dff614d5e0c5f61bb1ac94921c>, *P<lambda_3883c3dff614d5e0c5f61bb1ac94921c>;

struct <lambda_3883c3dff614d5e0c5f61bb1ac94921c> { /* PlaceHolder Structure */
};

typedef struct _s_CatchableType _s_CatchableType, *P_s_CatchableType;

struct _s_CatchableType { /* PlaceHolder Structure */
};

typedef enum __crt_lowio_text_mode {
} __crt_lowio_text_mode;

typedef struct <lambda_01a7098693036236037e7cdb9bca3d73> <lambda_01a7098693036236037e7cdb9bca3d73>, *P<lambda_01a7098693036236037e7cdb9bca3d73>;

struct <lambda_01a7098693036236037e7cdb9bca3d73> { /* PlaceHolder Structure */
};

typedef enum SLD_STATUS {
} SLD_STATUS;

typedef struct <lambda_1c23a5dd5e46d7c5fbe45428cfdcd388> <lambda_1c23a5dd5e46d7c5fbe45428cfdcd388>, *P<lambda_1c23a5dd5e46d7c5fbe45428cfdcd388>;

struct <lambda_1c23a5dd5e46d7c5fbe45428cfdcd388> { /* PlaceHolder Structure */
};

typedef struct __crt_stdio_stream __crt_stdio_stream, *P__crt_stdio_stream;

struct __crt_stdio_stream { /* PlaceHolder Structure */
};

typedef struct <lambda_13a597834fd3cef18bd4341e137232db> <lambda_13a597834fd3cef18bd4341e137232db>, *P<lambda_13a597834fd3cef18bd4341e137232db>;

struct <lambda_13a597834fd3cef18bd4341e137232db> { /* PlaceHolder Structure */
};

typedef struct __crt_win32_buffer<wchar_t,__crt_win32_buffer_no_resizing> __crt_win32_buffer<wchar_t,__crt_win32_buffer_no_resizing>, *P__crt_win32_buffer<wchar_t,__crt_win32_buffer_no_resizing>;

struct __crt_win32_buffer<wchar_t,__crt_win32_buffer_no_resizing> { /* PlaceHolder Structure */
};

typedef struct <lambda_1b3ad63c02abf531fe15530b52bade31> <lambda_1b3ad63c02abf531fe15530b52bade31>, *P<lambda_1b3ad63c02abf531fe15530b52bade31>;

struct <lambda_1b3ad63c02abf531fe15530b52bade31> { /* PlaceHolder Structure */
};

typedef struct <lambda_082dd7c0feb7dbdaf245f261e54a6583> <lambda_082dd7c0feb7dbdaf245f261e54a6583>, *P<lambda_082dd7c0feb7dbdaf245f261e54a6583>;

struct <lambda_082dd7c0feb7dbdaf245f261e54a6583> { /* PlaceHolder Structure */
};

typedef struct __crt_win32_buffer<wchar_t,__crt_win32_buffer_internal_dynamic_resizing> __crt_win32_buffer<wchar_t,__crt_win32_buffer_internal_dynamic_resizing>, *P__crt_win32_buffer<wchar_t,__crt_win32_buffer_internal_dynamic_resizing>;

struct __crt_win32_buffer<wchar_t,__crt_win32_buffer_internal_dynamic_resizing> { /* PlaceHolder Structure */
};

typedef struct __crt_multibyte_data __crt_multibyte_data, *P__crt_multibyte_data;

struct __crt_multibyte_data { /* PlaceHolder Structure */
};

typedef struct <lambda_9a32fed5bf61b6b509b2d3f6003082a1> <lambda_9a32fed5bf61b6b509b2d3f6003082a1>, *P<lambda_9a32fed5bf61b6b509b2d3f6003082a1>;

struct <lambda_9a32fed5bf61b6b509b2d3f6003082a1> { /* PlaceHolder Structure */
};

typedef struct IErrorInfo IErrorInfo, *PIErrorInfo;

struct IErrorInfo { /* PlaceHolder Structure */
};

typedef struct _s_ESTypeList _s_ESTypeList, *P_s_ESTypeList;

struct _s_ESTypeList { /* PlaceHolder Structure */
};

typedef struct <lambda_673ffc0dc9412a0afcf2088e0e1b9bdc> <lambda_673ffc0dc9412a0afcf2088e0e1b9bdc>, *P<lambda_673ffc0dc9412a0afcf2088e0e1b9bdc>;

struct <lambda_673ffc0dc9412a0afcf2088e0e1b9bdc> { /* PlaceHolder Structure */
};

typedef struct <lambda_d6a03b27cb314eb65d447ab85fffcbf2> <lambda_d6a03b27cb314eb65d447ab85fffcbf2>, *P<lambda_d6a03b27cb314eb65d447ab85fffcbf2>;

struct <lambda_d6a03b27cb314eb65d447ab85fffcbf2> { /* PlaceHolder Structure */
};

typedef enum XXH_alignment {
} XXH_alignment;

typedef struct <lambda_638799b9deba96c50f710eeac98168cd> <lambda_638799b9deba96c50f710eeac98168cd>, *P<lambda_638799b9deba96c50f710eeac98168cd>;

struct <lambda_638799b9deba96c50f710eeac98168cd> { /* PlaceHolder Structure */
};

typedef struct <lambda_156378f40168adef48d7ddfcff3a1264> <lambda_156378f40168adef48d7ddfcff3a1264>, *P<lambda_156378f40168adef48d7ddfcff3a1264>;

struct <lambda_156378f40168adef48d7ddfcff3a1264> { /* PlaceHolder Structure */
};

typedef struct __crt_deferred_errno_cache __crt_deferred_errno_cache, *P__crt_deferred_errno_cache;

struct __crt_deferred_errno_cache { /* PlaceHolder Structure */
};

typedef struct EHExceptionRecord EHExceptionRecord, *PEHExceptionRecord;

struct EHExceptionRecord { /* PlaceHolder Structure */
};

typedef enum __acrt_rounding_mode {
} __acrt_rounding_mode;

typedef struct <lambda_a993425e72f5bd8b40f5859286f153c4> <lambda_a993425e72f5bd8b40f5859286f153c4>, *P<lambda_a993425e72f5bd8b40f5859286f153c4>;

struct <lambda_a993425e72f5bd8b40f5859286f153c4> { /* PlaceHolder Structure */
};

typedef struct <lambda_8dff2cf36a5417162780cd64fa2883ef> <lambda_8dff2cf36a5417162780cd64fa2883ef>, *P<lambda_8dff2cf36a5417162780cd64fa2883ef>;

struct <lambda_8dff2cf36a5417162780cd64fa2883ef> { /* PlaceHolder Structure */
};

typedef struct <lambda_63911f43cc86614963252b1f423aad40> <lambda_63911f43cc86614963252b1f423aad40>, *P<lambda_63911f43cc86614963252b1f423aad40>;

struct <lambda_63911f43cc86614963252b1f423aad40> { /* PlaceHolder Structure */
};

typedef struct _xDISPATCHER_CONTEXT _xDISPATCHER_CONTEXT, *P_xDISPATCHER_CONTEXT;

struct _xDISPATCHER_CONTEXT { /* PlaceHolder Structure */
};

typedef struct <lambda_3a04bfe258a31910a526c90b4d849d20> <lambda_3a04bfe258a31910a526c90b4d849d20>, *P<lambda_3a04bfe258a31910a526c90b4d849d20>;

struct <lambda_3a04bfe258a31910a526c90b4d849d20> { /* PlaceHolder Structure */
};

typedef struct <lambda_ad9c22e73f4850e44729a5f831ae9ec1> <lambda_ad9c22e73f4850e44729a5f831ae9ec1>, *P<lambda_ad9c22e73f4850e44729a5f831ae9ec1>;

struct <lambda_ad9c22e73f4850e44729a5f831ae9ec1> { /* PlaceHolder Structure */
};

typedef struct <lambda_522ac1b1e1a1180d6f374a882b81d1c8> <lambda_522ac1b1e1a1180d6f374a882b81d1c8>, *P<lambda_522ac1b1e1a1180d6f374a882b81d1c8>;

struct <lambda_522ac1b1e1a1180d6f374a882b81d1c8> { /* PlaceHolder Structure */
};

typedef struct <lambda_d90129c13df834fdcbf8d2b88dafcf2d> <lambda_d90129c13df834fdcbf8d2b88dafcf2d>, *P<lambda_d90129c13df834fdcbf8d2b88dafcf2d>;

struct <lambda_d90129c13df834fdcbf8d2b88dafcf2d> { /* PlaceHolder Structure */
};

typedef struct <lambda_f6c7be5f7998530c34de24c7437d6b54> <lambda_f6c7be5f7998530c34de24c7437d6b54>, *P<lambda_f6c7be5f7998530c34de24c7437d6b54>;

struct <lambda_f6c7be5f7998530c34de24c7437d6b54> { /* PlaceHolder Structure */
};

typedef struct <lambda_36eeb330e99a4f0bf8a7da86d0894cb9> <lambda_36eeb330e99a4f0bf8a7da86d0894cb9>, *P<lambda_36eeb330e99a4f0bf8a7da86d0894cb9>;

struct <lambda_36eeb330e99a4f0bf8a7da86d0894cb9> { /* PlaceHolder Structure */
};

typedef struct _strflt _strflt, *P_strflt;

struct _strflt { /* PlaceHolder Structure */
};

typedef struct <lambda_38119f0e861e05405d8a144b9b982f0a> <lambda_38119f0e861e05405d8a144b9b982f0a>, *P<lambda_38119f0e861e05405d8a144b9b982f0a>;

struct <lambda_38119f0e861e05405d8a144b9b982f0a> { /* PlaceHolder Structure */
};

typedef struct __crt_lc_time_data __crt_lc_time_data, *P__crt_lc_time_data;

struct __crt_lc_time_data { /* PlaceHolder Structure */
};

typedef struct __acrt_ptd __acrt_ptd, *P__acrt_ptd;

struct __acrt_ptd { /* PlaceHolder Structure */
};

typedef struct __crt_locale_pointers __crt_locale_pointers, *P__crt_locale_pointers;

struct __crt_locale_pointers { /* PlaceHolder Structure */
};

typedef struct <lambda_1755787d260f86bf828f8bf7552b2658> <lambda_1755787d260f86bf828f8bf7552b2658>, *P<lambda_1755787d260f86bf828f8bf7552b2658>;

struct <lambda_1755787d260f86bf828f8bf7552b2658> { /* PlaceHolder Structure */
};

typedef struct <lambda_b4f66040be5f354a654fb75160c27bfc> <lambda_b4f66040be5f354a654fb75160c27bfc>, *P<lambda_b4f66040be5f354a654fb75160c27bfc>;

struct <lambda_b4f66040be5f354a654fb75160c27bfc> { /* PlaceHolder Structure */
};

typedef struct _stat64 _stat64, *P_stat64;

struct _stat64 { /* PlaceHolder Structure */
};

typedef struct <lambda_628dfdc04ba53c8bfc02c9951375f3f5> <lambda_628dfdc04ba53c8bfc02c9951375f3f5>, *P<lambda_628dfdc04ba53c8bfc02c9951375f3f5>;

struct <lambda_628dfdc04ba53c8bfc02c9951375f3f5> { /* PlaceHolder Structure */
};

typedef struct _Mtx_internal_imp_t _Mtx_internal_imp_t, *P_Mtx_internal_imp_t;

struct _Mtx_internal_imp_t { /* PlaceHolder Structure */
};

typedef struct <lambda_8d9723598c44aced2bc47669cc68e4e1> <lambda_8d9723598c44aced2bc47669cc68e4e1>, *P<lambda_8d9723598c44aced2bc47669cc68e4e1>;

struct <lambda_8d9723598c44aced2bc47669cc68e4e1> { /* PlaceHolder Structure */
};

typedef struct <lambda_7f2adfce497ff2baa965cd4f576ecfd1> <lambda_7f2adfce497ff2baa965cd4f576ecfd1>, *P<lambda_7f2adfce497ff2baa965cd4f576ecfd1>;

struct <lambda_7f2adfce497ff2baa965cd4f576ecfd1> { /* PlaceHolder Structure */
};

typedef struct <lambda_f4d89ce576adf8640f5662d60a8d4afb> <lambda_f4d89ce576adf8640f5662d60a8d4afb>, *P<lambda_f4d89ce576adf8640f5662d60a8d4afb>;

struct <lambda_f4d89ce576adf8640f5662d60a8d4afb> { /* PlaceHolder Structure */
};

typedef struct <lambda_410d79af7f07d98d83a3f525b3859a53> <lambda_410d79af7f07d98d83a3f525b3859a53>, *P<lambda_410d79af7f07d98d83a3f525b3859a53>;

struct <lambda_410d79af7f07d98d83a3f525b3859a53> { /* PlaceHolder Structure */
};

typedef struct <lambda_c376a267cfb53b6959b3b692ec76b120> <lambda_c376a267cfb53b6959b3b692ec76b120>, *P<lambda_c376a267cfb53b6959b3b692ec76b120>;

struct <lambda_c376a267cfb53b6959b3b692ec76b120> { /* PlaceHolder Structure */
};

typedef struct <lambda_22ebabd17bc4fa466a2aca6d8deb888d> <lambda_22ebabd17bc4fa466a2aca6d8deb888d>, *P<lambda_22ebabd17bc4fa466a2aca6d8deb888d>;

struct <lambda_22ebabd17bc4fa466a2aca6d8deb888d> { /* PlaceHolder Structure */
};

typedef struct <lambda_ab61a845afdef5b7c387490eaf3616ee> <lambda_ab61a845afdef5b7c387490eaf3616ee>, *P<lambda_ab61a845afdef5b7c387490eaf3616ee>;

struct <lambda_ab61a845afdef5b7c387490eaf3616ee> { /* PlaceHolder Structure */
};

typedef struct <lambda_3e61fc1153d2eec3991e8733eecb5419> <lambda_3e61fc1153d2eec3991e8733eecb5419>, *P<lambda_3e61fc1153d2eec3991e8733eecb5419>;

struct <lambda_3e61fc1153d2eec3991e8733eecb5419> { /* PlaceHolder Structure */
};

typedef struct __crt_win32_buffer<wchar_t,__crt_win32_buffer_public_dynamic_resizing> __crt_win32_buffer<wchar_t,__crt_win32_buffer_public_dynamic_resizing>, *P__crt_win32_buffer<wchar_t,__crt_win32_buffer_public_dynamic_resizing>;

struct __crt_win32_buffer<wchar_t,__crt_win32_buffer_public_dynamic_resizing> { /* PlaceHolder Structure */
};

typedef struct _Init_atexit _Init_atexit, *P_Init_atexit;

struct _Init_atexit { /* PlaceHolder Structure */
};

typedef struct <lambda_e3269ba96939e7713c73908c0d757d25> <lambda_e3269ba96939e7713c73908c0d757d25>, *P<lambda_e3269ba96939e7713c73908c0d757d25>;

struct <lambda_e3269ba96939e7713c73908c0d757d25> { /* PlaceHolder Structure */
};

typedef struct <lambda_b90d8f84996fccaedfcae156869b1630> <lambda_b90d8f84996fccaedfcae156869b1630>, *P<lambda_b90d8f84996fccaedfcae156869b1630>;

struct <lambda_b90d8f84996fccaedfcae156869b1630> { /* PlaceHolder Structure */
};

typedef struct <lambda_38ce7e780aa69e748d6df282ebc68efe> <lambda_38ce7e780aa69e748d6df282ebc68efe>, *P<lambda_38ce7e780aa69e748d6df282ebc68efe>;

struct <lambda_38ce7e780aa69e748d6df282ebc68efe> { /* PlaceHolder Structure */
};

typedef struct MRECmpImpl MRECmpImpl, *PMRECmpImpl;

struct MRECmpImpl { /* PlaceHolder Structure */
};

typedef struct __crt_seh_guarded_call<int> __crt_seh_guarded_call<int>, *P__crt_seh_guarded_call<int>;

struct __crt_seh_guarded_call<int> { /* PlaceHolder Structure */
};

typedef struct __crt_win32_buffer<char,__crt_win32_buffer_internal_dynamic_resizing> __crt_win32_buffer<char,__crt_win32_buffer_internal_dynamic_resizing>, *P__crt_win32_buffer<char,__crt_win32_buffer_internal_dynamic_resizing>;

struct __crt_win32_buffer<char,__crt_win32_buffer_internal_dynamic_resizing> { /* PlaceHolder Structure */
};

typedef struct <lambda_751a882b2c74d4b022dec766aa51a29a> <lambda_751a882b2c74d4b022dec766aa51a29a>, *P<lambda_751a882b2c74d4b022dec766aa51a29a>;

struct <lambda_751a882b2c74d4b022dec766aa51a29a> { /* PlaceHolder Structure */
};

typedef struct <lambda_6e4b09c48022b2350581041d5f6b0c4c> <lambda_6e4b09c48022b2350581041d5f6b0c4c>, *P<lambda_6e4b09c48022b2350581041d5f6b0c4c>;

struct <lambda_6e4b09c48022b2350581041d5f6b0c4c> { /* PlaceHolder Structure */
};

typedef struct xtime xtime, *Pxtime;

struct xtime { /* PlaceHolder Structure */
};

typedef struct __acrt_stdio_stream_mode __acrt_stdio_stream_mode, *P__acrt_stdio_stream_mode;

struct __acrt_stdio_stream_mode { /* PlaceHolder Structure */
};

typedef struct <lambda_ffc046909424fd52df0ac47e64813305> <lambda_ffc046909424fd52df0ac47e64813305>, *P<lambda_ffc046909424fd52df0ac47e64813305>;

struct <lambda_ffc046909424fd52df0ac47e64813305> { /* PlaceHolder Structure */
};

typedef struct <lambda_99fb1378e971ab6e7edea83e3a7a83a2> <lambda_99fb1378e971ab6e7edea83e3a7a83a2>, *P<lambda_99fb1378e971ab6e7edea83e3a7a83a2>;

struct <lambda_99fb1378e971ab6e7edea83e3a7a83a2> { /* PlaceHolder Structure */
};

typedef struct <lambda_5856287d7ecd2be6c9197bb4007c3f6e> <lambda_5856287d7ecd2be6c9197bb4007c3f6e>, *P<lambda_5856287d7ecd2be6c9197bb4007c3f6e>;

struct <lambda_5856287d7ecd2be6c9197bb4007c3f6e> { /* PlaceHolder Structure */
};

typedef enum XXH_endianess {
} XXH_endianess;

typedef enum _crt_exit_return_mode {
} _crt_exit_return_mode;

typedef struct _LocaleUpdate _LocaleUpdate, *P_LocaleUpdate;

struct _LocaleUpdate { /* PlaceHolder Structure */
};

typedef struct <lambda_6c6d19daa7c7d45df7f17119b7c25976> <lambda_6c6d19daa7c7d45df7f17119b7c25976>, *P<lambda_6c6d19daa7c7d45df7f17119b7c25976>;

struct <lambda_6c6d19daa7c7d45df7f17119b7c25976> { /* PlaceHolder Structure */
};

typedef struct <lambda_0bd0bd1e46f8138169959d81163ebf0c> <lambda_0bd0bd1e46f8138169959d81163ebf0c>, *P<lambda_0bd0bd1e46f8138169959d81163ebf0c>;

struct <lambda_0bd0bd1e46f8138169959d81163ebf0c> { /* PlaceHolder Structure */
};

typedef struct stream_input_adapter<wchar_t> stream_input_adapter<wchar_t>, *Pstream_input_adapter<wchar_t>;

struct stream_input_adapter<wchar_t> { /* PlaceHolder Structure */
};

typedef struct string_input_adapter<char> string_input_adapter<char>, *Pstring_input_adapter<char>;

struct string_input_adapter<char> { /* PlaceHolder Structure */
};

typedef struct scanset_buffer<wchar_t> scanset_buffer<wchar_t>, *Pscanset_buffer<wchar_t>;

struct scanset_buffer<wchar_t> { /* PlaceHolder Structure */
};

typedef struct string_input_adapter<wchar_t> string_input_adapter<wchar_t>, *Pstring_input_adapter<wchar_t>;

struct string_input_adapter<wchar_t> { /* PlaceHolder Structure */
};

typedef struct input_processor<wchar_t,__crt_stdio_input::stream_input_adapter<wchar_t>_> input_processor<wchar_t,__crt_stdio_input::stream_input_adapter<wchar_t>_>, *Pinput_processor<wchar_t,__crt_stdio_input::stream_input_adapter<wchar_t>_>;

struct input_processor<wchar_t,__crt_stdio_input::stream_input_adapter<wchar_t>_> { /* PlaceHolder Structure */
};

typedef struct input_processor<char,__crt_stdio_input::stream_input_adapter<char>_> input_processor<char,__crt_stdio_input::stream_input_adapter<char>_>, *Pinput_processor<char,__crt_stdio_input::stream_input_adapter<char>_>;

struct input_processor<char,__crt_stdio_input::stream_input_adapter<char>_> { /* PlaceHolder Structure */
};

typedef enum conversion_mode {
} conversion_mode;

typedef struct stream_input_adapter<char> stream_input_adapter<char>, *Pstream_input_adapter<char>;

struct stream_input_adapter<char> { /* PlaceHolder Structure */
};

typedef struct input_processor<char,__crt_stdio_input::string_input_adapter<char>_> input_processor<char,__crt_stdio_input::string_input_adapter<char>_>, *Pinput_processor<char,__crt_stdio_input::string_input_adapter<char>_>;

struct input_processor<char,__crt_stdio_input::string_input_adapter<char>_> { /* PlaceHolder Structure */
};

typedef struct format_string_parser<char> format_string_parser<char>, *Pformat_string_parser<char>;

struct format_string_parser<char> { /* PlaceHolder Structure */
};

typedef struct input_processor<wchar_t,__crt_stdio_input::string_input_adapter<wchar_t>_> input_processor<wchar_t,__crt_stdio_input::string_input_adapter<wchar_t>_>, *Pinput_processor<wchar_t,__crt_stdio_input::string_input_adapter<wchar_t>_>;

struct input_processor<wchar_t,__crt_stdio_input::string_input_adapter<wchar_t>_> { /* PlaceHolder Structure */
};

typedef struct format_string_parser<wchar_t> format_string_parser<wchar_t>, *Pformat_string_parser<wchar_t>;

struct format_string_parser<wchar_t> { /* PlaceHolder Structure */
};

typedef struct Camera Camera, *PCamera;

struct Camera { /* PlaceHolder Structure */
};

typedef struct Configuration Configuration, *PConfiguration;

struct Configuration { /* PlaceHolder Structure */
};

typedef enum SetConfigurationStatus {
} SetConfigurationStatus;

typedef struct process_handle_pair process_handle_pair, *Pprocess_handle_pair;

struct process_handle_pair { /* PlaceHolder Structure */
};

typedef struct output_processor<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>,__crt_stdio_output::positional_parameter_base<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>_>_> output_processor<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>,__crt_stdio_output::positional_parameter_base<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>_>_>, *Poutput_processor<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>,__crt_stdio_output::positional_parameter_base<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>_>_>;

struct output_processor<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>,__crt_stdio_output::positional_parameter_base<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>_>_> { /* PlaceHolder Structure */
};

typedef struct output_processor<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>,__crt_stdio_output::format_validation_base<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>_>_> output_processor<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>,__crt_stdio_output::format_validation_base<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>_>_>, *Poutput_processor<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>,__crt_stdio_output::format_validation_base<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>_>_>;

struct output_processor<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>,__crt_stdio_output::format_validation_base<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>_>_> { /* PlaceHolder Structure */
};

typedef struct output_adapter_common<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>_> output_adapter_common<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>_>, *Poutput_adapter_common<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>_>;

struct output_adapter_common<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>_> { /* PlaceHolder Structure */
};

typedef struct stream_output_adapter<char> stream_output_adapter<char>, *Pstream_output_adapter<char>;

struct stream_output_adapter<char> { /* PlaceHolder Structure */
};

typedef struct output_processor<char,__crt_stdio_output::stream_output_adapter<char>,__crt_stdio_output::positional_parameter_base<char,__crt_stdio_output::stream_output_adapter<char>_>_> output_processor<char,__crt_stdio_output::stream_output_adapter<char>,__crt_stdio_output::positional_parameter_base<char,__crt_stdio_output::stream_output_adapter<char>_>_>, *Poutput_processor<char,__crt_stdio_output::stream_output_adapter<char>,__crt_stdio_output::positional_parameter_base<char,__crt_stdio_output::stream_output_adapter<char>_>_>;

struct output_processor<char,__crt_stdio_output::stream_output_adapter<char>,__crt_stdio_output::positional_parameter_base<char,__crt_stdio_output::stream_output_adapter<char>_>_> { /* PlaceHolder Structure */
};

typedef struct stream_output_adapter<wchar_t> stream_output_adapter<wchar_t>, *Pstream_output_adapter<wchar_t>;

struct stream_output_adapter<wchar_t> { /* PlaceHolder Structure */
};

typedef enum length_modifier {
} length_modifier;

typedef struct formatting_buffer formatting_buffer, *Pformatting_buffer;

struct formatting_buffer { /* PlaceHolder Structure */
};

typedef struct output_processor<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>,__crt_stdio_output::standard_base<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>_>_> output_processor<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>,__crt_stdio_output::standard_base<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>_>_>, *Poutput_processor<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>,__crt_stdio_output::standard_base<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>_>_>;

struct output_processor<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>,__crt_stdio_output::standard_base<wchar_t,__crt_stdio_output::string_output_adapter<wchar_t>_>_> { /* PlaceHolder Structure */
};

typedef struct positional_parameter_base<char,__crt_stdio_output::string_output_adapter<char>_> positional_parameter_base<char,__crt_stdio_output::string_output_adapter<char>_>, *Ppositional_parameter_base<char,__crt_stdio_output::string_output_adapter<char>_>;

struct positional_parameter_base<char,__crt_stdio_output::string_output_adapter<char>_> { /* PlaceHolder Structure */
};

typedef struct output_processor<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>,__crt_stdio_output::positional_parameter_base<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>_>_> output_processor<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>,__crt_stdio_output::positional_parameter_base<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>_>_>, *Poutput_processor<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>,__crt_stdio_output::positional_parameter_base<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>_>_>;

struct output_processor<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>,__crt_stdio_output::positional_parameter_base<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>_>_> { /* PlaceHolder Structure */
};

typedef struct output_adapter_common<char,__crt_stdio_output::stream_output_adapter<char>_> output_adapter_common<char,__crt_stdio_output::stream_output_adapter<char>_>, *Poutput_adapter_common<char,__crt_stdio_output::stream_output_adapter<char>_>;

struct output_adapter_common<char,__crt_stdio_output::stream_output_adapter<char>_> { /* PlaceHolder Structure */
};

typedef struct output_processor<char,__crt_stdio_output::stream_output_adapter<char>,__crt_stdio_output::format_validation_base<char,__crt_stdio_output::stream_output_adapter<char>_>_> output_processor<char,__crt_stdio_output::stream_output_adapter<char>,__crt_stdio_output::format_validation_base<char,__crt_stdio_output::stream_output_adapter<char>_>_>, *Poutput_processor<char,__crt_stdio_output::stream_output_adapter<char>,__crt_stdio_output::format_validation_base<char,__crt_stdio_output::stream_output_adapter<char>_>_>;

struct output_processor<char,__crt_stdio_output::stream_output_adapter<char>,__crt_stdio_output::format_validation_base<char,__crt_stdio_output::stream_output_adapter<char>_>_> { /* PlaceHolder Structure */
};

typedef struct output_processor<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>,__crt_stdio_output::standard_base<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>_>_> output_processor<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>,__crt_stdio_output::standard_base<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>_>_>, *Poutput_processor<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>,__crt_stdio_output::standard_base<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>_>_>;

struct output_processor<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>,__crt_stdio_output::standard_base<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>_>_> { /* PlaceHolder Structure */
};

typedef struct string_output_adapter<char> string_output_adapter<char>, *Pstring_output_adapter<char>;

struct string_output_adapter<char> { /* PlaceHolder Structure */
};

typedef struct output_processor<char,__crt_stdio_output::string_output_adapter<char>,__crt_stdio_output::positional_parameter_base<char,__crt_stdio_output::string_output_adapter<char>_>_> output_processor<char,__crt_stdio_output::string_output_adapter<char>,__crt_stdio_output::positional_parameter_base<char,__crt_stdio_output::string_output_adapter<char>_>_>, *Poutput_processor<char,__crt_stdio_output::string_output_adapter<char>,__crt_stdio_output::positional_parameter_base<char,__crt_stdio_output::string_output_adapter<char>_>_>;

struct output_processor<char,__crt_stdio_output::string_output_adapter<char>,__crt_stdio_output::positional_parameter_base<char,__crt_stdio_output::string_output_adapter<char>_>_> { /* PlaceHolder Structure */
};

typedef struct output_processor<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>,__crt_stdio_output::format_validation_base<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>_>_> output_processor<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>,__crt_stdio_output::format_validation_base<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>_>_>, *Poutput_processor<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>,__crt_stdio_output::format_validation_base<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>_>_>;

struct output_processor<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>,__crt_stdio_output::format_validation_base<wchar_t,__crt_stdio_output::stream_output_adapter<wchar_t>_>_> { /* PlaceHolder Structure */
};

typedef struct output_processor<char,__crt_stdio_output::string_output_adapter<char>,__crt_stdio_output::standard_base<char,__crt_stdio_output::string_output_adapter<char>_>_> output_processor<char,__crt_stdio_output::string_output_adapter<char>,__crt_stdio_output::standard_base<char,__crt_stdio_output::string_output_adapter<char>_>_>, *Poutput_processor<char,__crt_stdio_output::string_output_adapter<char>,__crt_stdio_output::standard_base<char,__crt_stdio_output::string_output_adapter<char>_>_>;

struct output_processor<char,__crt_stdio_output::string_output_adapter<char>,__crt_stdio_output::standard_base<char,__crt_stdio_output::string_output_adapter<char>_>_> { /* PlaceHolder Structure */
};

typedef struct string_output_adapter<wchar_t> string_output_adapter<wchar_t>, *Pstring_output_adapter<wchar_t>;

struct string_output_adapter<wchar_t> { /* PlaceHolder Structure */
};

typedef struct positional_parameter_base<char,__crt_stdio_output::stream_output_adapter<char>_> positional_parameter_base<char,__crt_stdio_output::stream_output_adapter<char>_>, *Ppositional_parameter_base<char,__crt_stdio_output::stream_output_adapter<char>_>;

struct positional_parameter_base<char,__crt_stdio_output::stream_output_adapter<char>_> { /* PlaceHolder Structure */
};

typedef struct output_processor<char,__crt_stdio_output::string_output_adapter<char>,__crt_stdio_output::format_validation_base<char,__crt_stdio_output::string_output_adapter<char>_>_> output_processor<char,__crt_stdio_output::string_output_adapter<char>,__crt_stdio_output::format_validation_base<char,__crt_stdio_output::string_output_adapter<char>_>_>, *Poutput_processor<char,__crt_stdio_output::string_output_adapter<char>,__crt_stdio_output::format_validation_base<char,__crt_stdio_output::string_output_adapter<char>_>_>;

struct output_processor<char,__crt_stdio_output::string_output_adapter<char>,__crt_stdio_output::format_validation_base<char,__crt_stdio_output::string_output_adapter<char>_>_> { /* PlaceHolder Structure */
};

typedef struct output_processor<char,__crt_stdio_output::stream_output_adapter<char>,__crt_stdio_output::standard_base<char,__crt_stdio_output::stream_output_adapter<char>_>_> output_processor<char,__crt_stdio_output::stream_output_adapter<char>,__crt_stdio_output::standard_base<char,__crt_stdio_output::stream_output_adapter<char>_>_>, *Poutput_processor<char,__crt_stdio_output::stream_output_adapter<char>,__crt_stdio_output::standard_base<char,__crt_stdio_output::stream_output_adapter<char>_>_>;

struct output_processor<char,__crt_stdio_output::stream_output_adapter<char>,__crt_stdio_output::standard_base<char,__crt_stdio_output::stream_output_adapter<char>_>_> { /* PlaceHolder Structure */
};

typedef struct UMSFreeThreadProxyFactory UMSFreeThreadProxyFactory, *PUMSFreeThreadProxyFactory;

struct UMSFreeThreadProxyFactory { /* PlaceHolder Structure */
};

typedef enum module_id {
} module_id;

typedef enum function_id {
} function_id;

typedef struct _Yarn<char> _Yarn<char>, *P_Yarn<char>;

struct _Yarn<char> { /* PlaceHolder Structure */
};

typedef struct pair<MemBlock*___ptr64,MemBlock*___ptr64> pair<MemBlock*___ptr64,MemBlock*___ptr64>, *Ppair<MemBlock*___ptr64,MemBlock*___ptr64>;

struct pair<MemBlock*___ptr64,MemBlock*___ptr64> { /* PlaceHolder Structure */
};

typedef struct pair<REFMINIPDB2*___ptr64*___ptr64,REFMINIPDB2*___ptr64*___ptr64> pair<REFMINIPDB2*___ptr64*___ptr64,REFMINIPDB2*___ptr64*___ptr64>, *Ppair<REFMINIPDB2*___ptr64*___ptr64,REFMINIPDB2*___ptr64*___ptr64>;

struct pair<REFMINIPDB2*___ptr64*___ptr64,REFMINIPDB2*___ptr64*___ptr64> { /* PlaceHolder Structure */
};

typedef struct basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_> basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>, *Pbasic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>;

struct basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_> { /* PlaceHolder Structure */
};

typedef struct locale locale, *Plocale;

struct locale { /* PlaceHolder Structure */
};

typedef struct _Fac_tidy_reg_t _Fac_tidy_reg_t, *P_Fac_tidy_reg_t;

struct _Fac_tidy_reg_t { /* PlaceHolder Structure */
};

typedef struct basic_iostream<char,std::char_traits<char>_> basic_iostream<char,std::char_traits<char>_>, *Pbasic_iostream<char,std::char_traits<char>_>;

struct basic_iostream<char,std::char_traits<char>_> { /* PlaceHolder Structure */
};

typedef struct basic_string<char,std::char_traits<char>,std::allocator<char>_> basic_string<char,std::char_traits<char>,std::allocator<char>_>, *Pbasic_string<char,std::char_traits<char>,std::allocator<char>_>;

struct basic_string<char,std::char_traits<char>,std::allocator<char>_> { /* PlaceHolder Structure */
};

typedef struct _Init_locks _Init_locks, *P_Init_locks;

struct _Init_locks { /* PlaceHolder Structure */
};

typedef struct _Facet_base _Facet_base, *P_Facet_base;

struct _Facet_base { /* PlaceHolder Structure */
};

typedef struct _Locinfo _Locinfo, *P_Locinfo;

struct _Locinfo { /* PlaceHolder Structure */
};

typedef struct _Lockit _Lockit, *P_Lockit;

struct _Lockit { /* PlaceHolder Structure */
};

typedef struct write_result write_result, *Pwrite_result;

struct write_result { /* PlaceHolder Structure */
};

typedef struct UWMap4 UWMap4, *PUWMap4;

struct UWMap4 { /* PlaceHolder Structure */
};

typedef struct TryBlockMapEntry4 TryBlockMapEntry4, *PTryBlockMapEntry4;

struct TryBlockMapEntry4 { /* PlaceHolder Structure */
};

typedef struct HandlerMap4 HandlerMap4, *PHandlerMap4;

struct HandlerMap4 { /* PlaceHolder Structure */
};

typedef struct HandlerType4 HandlerType4, *PHandlerType4;

struct HandlerType4 { /* PlaceHolder Structure */
};

typedef struct TryBlockMap4 TryBlockMap4, *PTryBlockMap4;

struct TryBlockMap4 { /* PlaceHolder Structure */
};

typedef struct FuncInfo4 FuncInfo4, *PFuncInfo4;

struct FuncInfo4 { /* PlaceHolder Structure */
};

typedef struct iterator iterator, *Piterator;

struct iterator { /* PlaceHolder Structure */
};

typedef struct component_buffers<wchar_t> component_buffers<wchar_t>, *Pcomponent_buffers<wchar_t>;

struct component_buffers<wchar_t> { /* PlaceHolder Structure */
};

typedef struct argument_list<char> argument_list<char>, *Pargument_list<char>;

struct argument_list<char> { /* PlaceHolder Structure */
};

typedef struct input_adapter_character_source<__crt_stdio_input::string_input_adapter<wchar_t>_> input_adapter_character_source<__crt_stdio_input::string_input_adapter<wchar_t>_>, *Pinput_adapter_character_source<__crt_stdio_input::string_input_adapter<wchar_t>_>;

struct input_adapter_character_source<__crt_stdio_input::string_input_adapter<wchar_t>_> { /* PlaceHolder Structure */
};

typedef struct input_adapter_character_source<__crt_stdio_input::stream_input_adapter<char>_> input_adapter_character_source<__crt_stdio_input::stream_input_adapter<char>_>, *Pinput_adapter_character_source<__crt_stdio_input::stream_input_adapter<char>_>;

struct input_adapter_character_source<__crt_stdio_input::stream_input_adapter<char>_> { /* PlaceHolder Structure */
};

typedef struct big_integer big_integer, *Pbig_integer;

struct big_integer { /* PlaceHolder Structure */
};

typedef struct c_string_character_source<wchar_t> c_string_character_source<wchar_t>, *Pc_string_character_source<wchar_t>;

struct c_string_character_source<wchar_t> { /* PlaceHolder Structure */
};

typedef enum floating_point_parse_result {
} floating_point_parse_result;

typedef struct c_string_character_source<char> c_string_character_source<char>, *Pc_string_character_source<char>;

struct c_string_character_source<char> { /* PlaceHolder Structure */
};

typedef struct floating_point_string floating_point_string, *Pfloating_point_string;

struct floating_point_string { /* PlaceHolder Structure */
};

typedef struct input_adapter_character_source<__crt_stdio_input::stream_input_adapter<wchar_t>_> input_adapter_character_source<__crt_stdio_input::stream_input_adapter<wchar_t>_>, *Pinput_adapter_character_source<__crt_stdio_input::stream_input_adapter<wchar_t>_>;

struct input_adapter_character_source<__crt_stdio_input::stream_input_adapter<wchar_t>_> { /* PlaceHolder Structure */
};

typedef struct floating_point_value floating_point_value, *Pfloating_point_value;

struct floating_point_value { /* PlaceHolder Structure */
};

typedef struct input_adapter_character_source<__crt_stdio_input::string_input_adapter<char>_> input_adapter_character_source<__crt_stdio_input::string_input_adapter<char>_>, *Pinput_adapter_character_source<__crt_stdio_input::string_input_adapter<char>_>;

struct input_adapter_character_source<__crt_stdio_input::string_input_adapter<char>_> { /* PlaceHolder Structure */
};

typedef enum buffer_id {
} buffer_id;

typedef int (*_onexit_t)(void);

typedef void (*_invalid_parameter_handler)(wchar_t *, wchar_t *, wchar_t *, uint, uintptr_t);

typedef struct _cpinfo _cpinfo, *P_cpinfo;

struct _cpinfo {
    UINT MaxCharSize;
    BYTE DefaultChar[2];
    BYTE LeadByte[12];
};

typedef BOOL (*LOCALE_ENUMPROCW)(LPWSTR);

typedef struct _nlsversioninfo _nlsversioninfo, *P_nlsversioninfo;

typedef struct _nlsversioninfo *LPNLSVERSIONINFO;

struct _nlsversioninfo {
    DWORD dwNLSVersionInfoSize;
    DWORD dwNLSVersion;
    DWORD dwDefinedVersion;
};

typedef struct _cpinfo *LPCPINFO;

typedef DWORD LCTYPE;

typedef struct tagSOLE_AUTHENTICATION_SERVICE tagSOLE_AUTHENTICATION_SERVICE, *PtagSOLE_AUTHENTICATION_SERVICE;

typedef struct tagSOLE_AUTHENTICATION_SERVICE SOLE_AUTHENTICATION_SERVICE;

typedef long HRESULT;

struct tagSOLE_AUTHENTICATION_SERVICE {
    DWORD dwAuthnSvc;
    DWORD dwAuthzSvc;
    OLECHAR *pPrincipalName;
    HRESULT hr;
};

typedef struct _DISPATCHER_CONTEXT _DISPATCHER_CONTEXT, *P_DISPATCHER_CONTEXT;

struct _DISPATCHER_CONTEXT {
};

typedef enum _EXCEPTION_DISPOSITION {
    ExceptionContinueExecution=0,
    ExceptionContinueSearch=1,
    ExceptionNestedException=2,
    ExceptionCollidedUnwind=3
} _EXCEPTION_DISPOSITION;

typedef enum _EXCEPTION_DISPOSITION EXCEPTION_DISPOSITION;

typedef struct DotNetPdbInfo DotNetPdbInfo, *PDotNetPdbInfo;

struct DotNetPdbInfo {
    char signature[4];
    GUID guid;
    dword age;
    char pdbpath[38];
};

typedef struct _SETJMP_FLOAT128 _SETJMP_FLOAT128, *P_SETJMP_FLOAT128;

typedef struct _SETJMP_FLOAT128 SETJMP_FLOAT128;

typedef SETJMP_FLOAT128 _JBTYPE;

struct _SETJMP_FLOAT128 {
    ulonglong Part[2];
};

typedef struct _CONSOLE_READCONSOLE_CONTROL _CONSOLE_READCONSOLE_CONTROL, *P_CONSOLE_READCONSOLE_CONTROL;

struct _CONSOLE_READCONSOLE_CONTROL {
    ULONG nLength;
    ULONG nInitialChars;
    ULONG dwCtrlWakeupMask;
    ULONG dwControlKeyState;
};

typedef struct _CONSOLE_READCONSOLE_CONTROL *PCONSOLE_READCONSOLE_CONTROL;

typedef PVOID HDEVINFO;

typedef struct _SP_DEVICE_INTERFACE_DATA _SP_DEVICE_INTERFACE_DATA, *P_SP_DEVICE_INTERFACE_DATA;


/* WARNING! conflicting data type names: /guiddef.h/GUID - /GUID */

struct _SP_DEVICE_INTERFACE_DATA {
    DWORD cbSize;
    GUID InterfaceClassGuid;
    DWORD Flags;
    ULONG_PTR Reserved;
};

typedef struct _SP_DEVICE_INTERFACE_DETAIL_DATA_W _SP_DEVICE_INTERFACE_DETAIL_DATA_W, *P_SP_DEVICE_INTERFACE_DETAIL_DATA_W;

struct _SP_DEVICE_INTERFACE_DETAIL_DATA_W {
    DWORD cbSize;
    WCHAR DevicePath[1];
};

typedef struct _SP_DEVINFO_DATA _SP_DEVINFO_DATA, *P_SP_DEVINFO_DATA;

struct _SP_DEVINFO_DATA {
    DWORD cbSize;
    GUID ClassGuid;
    DWORD DevInst;
    ULONG_PTR Reserved;
};

typedef struct _SP_DEVICE_INTERFACE_DETAIL_DATA_W *PSP_DEVICE_INTERFACE_DETAIL_DATA_W;

typedef struct _SP_DEVICE_INTERFACE_DATA *PSP_DEVICE_INTERFACE_DATA;

typedef struct _SP_DEVINFO_DATA *PSP_DEVINFO_DATA;

typedef struct lconv lconv, *Plconv;

struct lconv {
    char *decimal_point;
    char *thousands_sep;
    char *grouping;
    char *int_curr_symbol;
    char *currency_symbol;
    char *mon_decimal_point;
    char *mon_thousands_sep;
    char *mon_grouping;
    char *positive_sign;
    char *negative_sign;
    char int_frac_digits;
    char frac_digits;
    char p_cs_precedes;
    char p_sep_by_space;
    char n_cs_precedes;
    char n_sep_by_space;
    char p_sign_posn;
    char n_sign_posn;
    wchar_t *_W_decimal_point;
    wchar_t *_W_thousands_sep;
    wchar_t *_W_int_curr_symbol;
    wchar_t *_W_currency_symbol;
    wchar_t *_W_mon_decimal_point;
    wchar_t *_W_mon_thousands_sep;
    wchar_t *_W_positive_sign;
    wchar_t *_W_negative_sign;
};

typedef ushort wint_t;

typedef long __time32_t;

typedef struct localerefcount localerefcount, *Plocalerefcount;

typedef struct localerefcount locrefcount;

struct localerefcount {
    char *locale;
    wchar_t *wlocale;
    int *refcount;
    int *wrefcount;
};

typedef ulonglong size_t;

typedef int errno_t;

typedef struct localeinfo_struct localeinfo_struct, *Plocaleinfo_struct;

typedef struct localeinfo_struct *_locale_t;

typedef struct threadlocaleinfostruct threadlocaleinfostruct, *Pthreadlocaleinfostruct;

typedef struct threadlocaleinfostruct *pthreadlocinfo;

typedef struct threadmbcinfostruct threadmbcinfostruct, *Pthreadmbcinfostruct;

typedef struct threadmbcinfostruct *pthreadmbcinfo;

typedef struct __lc_time_data __lc_time_data, *P__lc_time_data;

struct threadlocaleinfostruct {
    int refcount;
    uint lc_codepage;
    uint lc_collate_cp;
    uint lc_time_cp;
    locrefcount lc_category[6];
    int lc_clike;
    int mb_cur_max;
    int *lconv_intl_refcount;
    int *lconv_num_refcount;
    int *lconv_mon_refcount;
    struct lconv *lconv;
    int *ctype1_refcount;
    ushort *ctype1;
    ushort *pctype;
    uchar *pclmap;
    uchar *pcumap;
    struct __lc_time_data *lc_time_curr;
    wchar_t *locale_name[6];
};

struct threadmbcinfostruct {
    int refcount;
    int mbcodepage;
    int ismbcodepage;
    ushort mbulinfo[6];
    uchar mbctype[257];
    uchar mbcasemap[256];
    wchar_t *mblocalename;
};

struct localeinfo_struct {
    pthreadlocinfo locinfo;
    pthreadmbcinfo mbcinfo;
};

struct __lc_time_data {
    char *wday_abbr[7];
    char *wday[7];
    char *month_abbr[12];
    char *month[12];
    char *ampm[2];
    char *ww_sdatefmt;
    char *ww_ldatefmt;
    char *ww_timefmt;
    int ww_caltype;
    int refcount;
    wchar_t *_W_wday_abbr[7];
    wchar_t *_W_wday[7];
    wchar_t *_W_month_abbr[12];
    wchar_t *_W_month[12];
    wchar_t *_W_ampm[2];
    wchar_t *_W_ww_sdatefmt;
    wchar_t *_W_ww_ldatefmt;
    wchar_t *_W_ww_timefmt;
    wchar_t *_W_ww_locale_name;
};

typedef longlong __time64_t;

typedef longlong intptr_t;

typedef size_t rsize_t;

typedef ushort wctype_t;

typedef struct _GUID _GUID, *P_GUID;

struct _GUID {
    ulong Data1;
    ushort Data2;
    ushort Data3;
    uchar Data4[8];
};

typedef GUID IID;

typedef enum enum_696 {
    DISPLAYCONFIG_PIXELFORMAT_FORCE_UINT32=-1,
    DISPLAYCONFIG_PIXELFORMAT_8BPP=1,
    DISPLAYCONFIG_PIXELFORMAT_16BPP=2,
    DISPLAYCONFIG_PIXELFORMAT_24BPP=3,
    DISPLAYCONFIG_PIXELFORMAT_32BPP=4,
    DISPLAYCONFIG_PIXELFORMAT_NONGDI=5
} enum_696;

typedef enum enum_695 {
    DISPLAYCONFIG_MODE_INFO_TYPE_FORCE_UINT32=-1,
    DISPLAYCONFIG_MODE_INFO_TYPE_SOURCE=1,
    DISPLAYCONFIG_MODE_INFO_TYPE_TARGET=2
} enum_695;

typedef enum enum_694 {
    DISPLAYCONFIG_ROTATION_FORCE_UINT32=-1,
    DISPLAYCONFIG_ROTATION_IDENTITY=1,
    DISPLAYCONFIG_ROTATION_ROTATE90=2,
    DISPLAYCONFIG_ROTATION_ROTATE180=3,
    DISPLAYCONFIG_ROTATION_ROTATE270=4
} enum_694;

typedef enum enum_693 {
    DISPLAYCONFIG_SCALING_FORCE_UINT32=-1,
    DISPLAYCONFIG_SCALING_IDENTITY=1,
    DISPLAYCONFIG_SCALING_CENTERED=2,
    DISPLAYCONFIG_SCALING_STRETCHED=3,
    DISPLAYCONFIG_SCALING_ASPECTRATIOCENTEREDMAX=4,
    DISPLAYCONFIG_SCALING_CUSTOM=5,
    DISPLAYCONFIG_SCALING_PREFERRED=128
} enum_693;

typedef struct _DISPLAY_DEVICEW _DISPLAY_DEVICEW, *P_DISPLAY_DEVICEW;

struct _DISPLAY_DEVICEW {
    DWORD cb;
    WCHAR DeviceName[32];
    WCHAR DeviceString[128];
    DWORD StateFlags;
    WCHAR DeviceID[128];
    WCHAR DeviceKey[128];
};

typedef struct _devicemodeW _devicemodeW, *P_devicemodeW;

typedef union _union_682 _union_682, *P_union_682;

typedef union _union_685 _union_685, *P_union_685;

typedef struct _struct_683 _struct_683, *P_struct_683;

typedef struct _struct_684 _struct_684, *P_struct_684;

typedef struct _POINTL _POINTL, *P_POINTL;

typedef struct _POINTL POINTL;

struct _POINTL {
    LONG x;
    LONG y;
};

union _union_685 {
    DWORD dmDisplayFlags;
    DWORD dmNup;
};

struct _struct_684 {
    POINTL dmPosition;
    DWORD dmDisplayOrientation;
    DWORD dmDisplayFixedOutput;
};

struct _struct_683 {
    short dmOrientation;
    short dmPaperSize;
    short dmPaperLength;
    short dmPaperWidth;
    short dmScale;
    short dmCopies;
    short dmDefaultSource;
    short dmPrintQuality;
};

union _union_682 {
    struct _struct_683 field0;
    struct _struct_684 field1;
};

struct _devicemodeW {
    WCHAR dmDeviceName[32];
    WORD dmSpecVersion;
    WORD dmDriverVersion;
    WORD dmSize;
    WORD dmDriverExtra;
    DWORD dmFields;
    union _union_682 field6_0x4c;
    short dmColor;
    short dmDuplex;
    short dmYResolution;
    short dmTTOption;
    short dmCollate;
    WCHAR dmFormName[32];
    WORD dmLogPixels;
    DWORD dmBitsPerPel;
    DWORD dmPelsWidth;
    DWORD dmPelsHeight;
    union _union_685 field17_0xb4;
    DWORD dmDisplayFrequency;
    DWORD dmICMMethod;
    DWORD dmICMIntent;
    DWORD dmMediaType;
    DWORD dmDitherType;
    DWORD dmReserved1;
    DWORD dmReserved2;
    DWORD dmPanningWidth;
    DWORD dmPanningHeight;
};

typedef struct _devicemodeW DEVMODEW;

typedef struct _DISPLAY_DEVICEW *PDISPLAY_DEVICEW;

typedef enum enum_690 {
    DISPLAYCONFIG_SCANLINE_ORDERING_FORCE_UINT32=-1,
    DISPLAYCONFIG_SCANLINE_ORDERING_UNSPECIFIED=0,
    DISPLAYCONFIG_SCANLINE_ORDERING_PROGRESSIVE=1,
    DISPLAYCONFIG_SCANLINE_ORDERING_INTERLACED=2,
    DISPLAYCONFIG_SCANLINE_ORDERING_INTERLACED_LOWERFIELDFIRST=3,
    DISPLAYCONFIG_SCANLINE_ORDERING_INTERLACED_UPPERFIELDFIRST=3
} enum_690;

typedef enum enum_690 DISPLAYCONFIG_SCANLINE_ORDERING;

typedef struct DISPLAYCONFIG_PATH_TARGET_INFO DISPLAYCONFIG_PATH_TARGET_INFO, *PDISPLAYCONFIG_PATH_TARGET_INFO;

typedef struct _LUID _LUID, *P_LUID;

typedef struct _LUID LUID;

typedef enum enum_689 {
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_INTERNAL=-2147483648,
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_FORCE_UINT32=-1,
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_OTHER=-1,
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_HD15=0,
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_SVIDEO=1,
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_COMPOSITE_VIDEO=2,
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_COMPONENT_VIDEO=3,
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_DVI=4,
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_HDMI=5,
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_LVDS=6,
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_D_JPN=8,
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_SDI=9,
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_DISPLAYPORT_EXTERNAL=10,
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_DISPLAYPORT_EMBEDDED=11,
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_UDI_EXTERNAL=12,
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_UDI_EMBEDDED=13,
    DISPLAYCONFIG_OUTPUT_TECHNOLOGY_SDTVDONGLE=14
} enum_689;

typedef enum enum_689 DISPLAYCONFIG_VIDEO_OUTPUT_TECHNOLOGY;

typedef enum enum_694 DISPLAYCONFIG_ROTATION;

typedef enum enum_693 DISPLAYCONFIG_SCALING;

typedef struct DISPLAYCONFIG_RATIONAL DISPLAYCONFIG_RATIONAL, *PDISPLAYCONFIG_RATIONAL;

struct _LUID {
    DWORD LowPart;
    LONG HighPart;
};

struct DISPLAYCONFIG_RATIONAL {
    UINT32 Numerator;
    UINT32 Denominator;
};

struct DISPLAYCONFIG_PATH_TARGET_INFO {
    LUID adapterId;
    UINT32 id;
    UINT32 modeInfoIdx;
    DISPLAYCONFIG_VIDEO_OUTPUT_TECHNOLOGY outputTechnology;
    DISPLAYCONFIG_ROTATION rotation;
    DISPLAYCONFIG_SCALING scaling;
    struct DISPLAYCONFIG_RATIONAL refreshRate;
    DISPLAYCONFIG_SCANLINE_ORDERING scanLineOrdering;
    BOOL targetAvailable;
    UINT32 statusFlags;
};

typedef struct _devicemodeA _devicemodeA, *P_devicemodeA;

typedef union _union_677 _union_677, *P_union_677;

typedef union _union_680 _union_680, *P_union_680;

typedef struct _struct_678 _struct_678, *P_struct_678;

typedef struct _struct_679 _struct_679, *P_struct_679;

struct _struct_679 {
    POINTL dmPosition;
    DWORD dmDisplayOrientation;
    DWORD dmDisplayFixedOutput;
};

struct _struct_678 {
    short dmOrientation;
    short dmPaperSize;
    short dmPaperLength;
    short dmPaperWidth;
    short dmScale;
    short dmCopies;
    short dmDefaultSource;
    short dmPrintQuality;
};

union _union_677 {
    struct _struct_678 field0;
    struct _struct_679 field1;
};

union _union_680 {
    DWORD dmDisplayFlags;
    DWORD dmNup;
};

struct _devicemodeA {
    BYTE dmDeviceName[32];
    WORD dmSpecVersion;
    WORD dmDriverVersion;
    WORD dmSize;
    WORD dmDriverExtra;
    DWORD dmFields;
    union _union_677 field6_0x2c;
    short dmColor;
    short dmDuplex;
    short dmYResolution;
    short dmTTOption;
    short dmCollate;
    BYTE dmFormName[32];
    WORD dmLogPixels;
    DWORD dmBitsPerPel;
    DWORD dmPelsWidth;
    DWORD dmPelsHeight;
    union _union_680 field17_0x74;
    DWORD dmDisplayFrequency;
    DWORD dmICMMethod;
    DWORD dmICMIntent;
    DWORD dmMediaType;
    DWORD dmDitherType;
    DWORD dmReserved1;
    DWORD dmReserved2;
    DWORD dmPanningWidth;
    DWORD dmPanningHeight;
};

typedef struct DISPLAYCONFIG_2DREGION DISPLAYCONFIG_2DREGION, *PDISPLAYCONFIG_2DREGION;

struct DISPLAYCONFIG_2DREGION {
    UINT32 cx;
    UINT32 cy;
};

typedef struct _devicemodeA DEVMODEA;

typedef enum enum_705 {
    DISPLAYCONFIG_DEVICE_INFO_FORCE_UINT32=-1,
    DISPLAYCONFIG_DEVICE_INFO_GET_SOURCE_NAME=1,
    DISPLAYCONFIG_DEVICE_INFO_GET_TARGET_NAME=2,
    DISPLAYCONFIG_DEVICE_INFO_GET_TARGET_PREFERRED_MODE=3,
    DISPLAYCONFIG_DEVICE_INFO_GET_ADAPTER_NAME=4,
    DISPLAYCONFIG_DEVICE_INFO_SET_TARGET_PERSISTENCE=5
} enum_705;

typedef enum enum_705 DISPLAYCONFIG_DEVICE_INFO_TYPE;

typedef struct DISPLAYCONFIG_PATH_INFO DISPLAYCONFIG_PATH_INFO, *PDISPLAYCONFIG_PATH_INFO;

typedef struct DISPLAYCONFIG_PATH_SOURCE_INFO DISPLAYCONFIG_PATH_SOURCE_INFO, *PDISPLAYCONFIG_PATH_SOURCE_INFO;

struct DISPLAYCONFIG_PATH_SOURCE_INFO {
    LUID adapterId;
    UINT32 id;
    UINT32 modeInfoIdx;
    UINT32 statusFlags;
};

struct DISPLAYCONFIG_PATH_INFO {
    struct DISPLAYCONFIG_PATH_SOURCE_INFO sourceInfo;
    struct DISPLAYCONFIG_PATH_TARGET_INFO targetInfo;
    UINT32 flags;
};

typedef struct DISPLAYCONFIG_TARGET_MODE DISPLAYCONFIG_TARGET_MODE, *PDISPLAYCONFIG_TARGET_MODE;

typedef struct DISPLAYCONFIG_VIDEO_SIGNAL_INFO DISPLAYCONFIG_VIDEO_SIGNAL_INFO, *PDISPLAYCONFIG_VIDEO_SIGNAL_INFO;

struct DISPLAYCONFIG_VIDEO_SIGNAL_INFO {
    UINT64 pixelRate;
    struct DISPLAYCONFIG_RATIONAL hSyncFreq;
    struct DISPLAYCONFIG_RATIONAL vSyncFreq;
    struct DISPLAYCONFIG_2DREGION activeSize;
    struct DISPLAYCONFIG_2DREGION totalSize;
    UINT32 videoStandard;
    DISPLAYCONFIG_SCANLINE_ORDERING scanLineOrdering;
};

struct DISPLAYCONFIG_TARGET_MODE {
    struct DISPLAYCONFIG_VIDEO_SIGNAL_INFO targetVideoSignalInfo;
};

typedef enum enum_704 {
    DISPLAYCONFIG_TOPOLOGY_FORCE_UINT32=-1,
    DISPLAYCONFIG_TOPOLOGY_INTERNAL=1,
    DISPLAYCONFIG_TOPOLOGY_CLONE=2,
    DISPLAYCONFIG_TOPOLOGY_EXTEND=4,
    DISPLAYCONFIG_TOPOLOGY_EXTERNAL=8
} enum_704;

typedef enum enum_704 DISPLAYCONFIG_TOPOLOGY_ID;

typedef struct DISPLAYCONFIG_SOURCE_MODE DISPLAYCONFIG_SOURCE_MODE, *PDISPLAYCONFIG_SOURCE_MODE;

typedef enum enum_696 DISPLAYCONFIG_PIXELFORMAT;

struct DISPLAYCONFIG_SOURCE_MODE {
    UINT32 width;
    UINT32 height;
    DISPLAYCONFIG_PIXELFORMAT pixelFormat;
    POINTL position;
};

typedef enum enum_695 DISPLAYCONFIG_MODE_INFO_TYPE;

typedef struct DISPLAYCONFIG_DEVICE_INFO_HEADER DISPLAYCONFIG_DEVICE_INFO_HEADER, *PDISPLAYCONFIG_DEVICE_INFO_HEADER;

struct DISPLAYCONFIG_DEVICE_INFO_HEADER {
    DISPLAYCONFIG_DEVICE_INFO_TYPE type;
    UINT32 size;
    LUID adapterId;
    UINT32 id;
};

typedef struct DISPLAYCONFIG_MODE_INFO DISPLAYCONFIG_MODE_INFO, *PDISPLAYCONFIG_MODE_INFO;

typedef union _union_700 _union_700, *P_union_700;

union _union_700 {
    struct DISPLAYCONFIG_TARGET_MODE targetMode;
    struct DISPLAYCONFIG_SOURCE_MODE sourceMode;
};

struct DISPLAYCONFIG_MODE_INFO {
    DISPLAYCONFIG_MODE_INFO_TYPE infoType;
    UINT32 id;
    LUID adapterId;
    union _union_700 field3_0x10;
};

typedef void *RPC_AUTH_IDENTITY_HANDLE;

typedef uchar *RPC_CSTR;

typedef GUID UUID;

typedef PVOID BCRYPT_KEY_HANDLE;

typedef PVOID BCRYPT_HANDLE;

typedef PVOID BCRYPT_HASH_HANDLE;

typedef PVOID BCRYPT_ALG_HANDLE;

typedef LONG NTSTATUS;

typedef long RPC_STATUS;

typedef struct _SYSTEM_LOGICAL_PROCESSOR_INFORMATION _SYSTEM_LOGICAL_PROCESSOR_INFORMATION, *P_SYSTEM_LOGICAL_PROCESSOR_INFORMATION;

typedef struct _SYSTEM_LOGICAL_PROCESSOR_INFORMATION *PSYSTEM_LOGICAL_PROCESSOR_INFORMATION;

typedef enum _LOGICAL_PROCESSOR_RELATIONSHIP {
    RelationProcessorCore=0,
    RelationNumaNode=1,
    RelationCache=2,
    RelationProcessorPackage=3,
    RelationGroup=4,
    RelationAll=65535
} _LOGICAL_PROCESSOR_RELATIONSHIP;

typedef enum _LOGICAL_PROCESSOR_RELATIONSHIP LOGICAL_PROCESSOR_RELATIONSHIP;

typedef union _union_160 _union_160, *P_union_160;

typedef struct _struct_161 _struct_161, *P_struct_161;

typedef struct _struct_162 _struct_162, *P_struct_162;

typedef struct _CACHE_DESCRIPTOR _CACHE_DESCRIPTOR, *P_CACHE_DESCRIPTOR;

typedef struct _CACHE_DESCRIPTOR CACHE_DESCRIPTOR;

typedef enum _PROCESSOR_CACHE_TYPE {
    CacheUnified=0,
    CacheInstruction=1,
    CacheData=2,
    CacheTrace=3
} _PROCESSOR_CACHE_TYPE;

typedef enum _PROCESSOR_CACHE_TYPE PROCESSOR_CACHE_TYPE;

struct _struct_162 {
    DWORD NodeNumber;
};

struct _struct_161 {
    BYTE Flags;
};

struct _CACHE_DESCRIPTOR {
    BYTE Level;
    BYTE Associativity;
    WORD LineSize;
    DWORD Size;
    PROCESSOR_CACHE_TYPE Type;
};

union _union_160 {
    struct _struct_161 ProcessorCore;
    struct _struct_162 NumaNode;
    CACHE_DESCRIPTOR Cache;
    ULONGLONG Reserved[2];
};

struct _SYSTEM_LOGICAL_PROCESSOR_INFORMATION {
    ULONG_PTR ProcessorMask;
    LOGICAL_PROCESSOR_RELATIONSHIP Relationship;
    union _union_160 u;
};

typedef union _ULARGE_INTEGER _ULARGE_INTEGER, *P_ULARGE_INTEGER;

typedef union _ULARGE_INTEGER ULARGE_INTEGER;

typedef struct _struct_22 _struct_22, *P_struct_22;

typedef struct _struct_23 _struct_23, *P_struct_23;

struct _struct_23 {
    DWORD LowPart;
    DWORD HighPart;
};

struct _struct_22 {
    DWORD LowPart;
    DWORD HighPart;
};

union _ULARGE_INTEGER {
    struct _struct_22 s;
    struct _struct_23 u;
    ULONGLONG QuadPart;
};

typedef PVOID PSECURITY_DESCRIPTOR;

typedef struct _TOKEN_PRIVILEGES _TOKEN_PRIVILEGES, *P_TOKEN_PRIVILEGES;

typedef struct _LUID_AND_ATTRIBUTES _LUID_AND_ATTRIBUTES, *P_LUID_AND_ATTRIBUTES;

typedef struct _LUID_AND_ATTRIBUTES LUID_AND_ATTRIBUTES;

struct _LUID_AND_ATTRIBUTES {
    LUID Luid;
    DWORD Attributes;
};

struct _TOKEN_PRIVILEGES {
    DWORD PrivilegeCount;
    LUID_AND_ATTRIBUTES Privileges[1];
};

typedef struct _RUNTIME_FUNCTION _RUNTIME_FUNCTION, *P_RUNTIME_FUNCTION;

struct _RUNTIME_FUNCTION {
    DWORD BeginAddress;
    DWORD EndAddress;
    DWORD UnwindData;
};

typedef struct _RUNTIME_FUNCTION *PRUNTIME_FUNCTION;

typedef struct _UNWIND_HISTORY_TABLE_ENTRY _UNWIND_HISTORY_TABLE_ENTRY, *P_UNWIND_HISTORY_TABLE_ENTRY;

typedef struct _UNWIND_HISTORY_TABLE_ENTRY UNWIND_HISTORY_TABLE_ENTRY;

struct _UNWIND_HISTORY_TABLE_ENTRY {
    DWORD64 ImageBase;
    PRUNTIME_FUNCTION FunctionEntry;
};

typedef union _union_61 _union_61, *P_union_61;

typedef struct _M128A *PM128A;

typedef struct _struct_62 _struct_62, *P_struct_62;

struct _struct_62 {
    PM128A Xmm0;
    PM128A Xmm1;
    PM128A Xmm2;
    PM128A Xmm3;
    PM128A Xmm4;
    PM128A Xmm5;
    PM128A Xmm6;
    PM128A Xmm7;
    PM128A Xmm8;
    PM128A Xmm9;
    PM128A Xmm10;
    PM128A Xmm11;
    PM128A Xmm12;
    PM128A Xmm13;
    PM128A Xmm14;
    PM128A Xmm15;
};

union _union_61 {
    PM128A FloatingContext[16];
    struct _struct_62 s;
};

typedef union _union_63 _union_63, *P_union_63;

typedef struct _struct_64 _struct_64, *P_struct_64;

struct _struct_64 {
    PDWORD64 Rax;
    PDWORD64 Rcx;
    PDWORD64 Rdx;
    PDWORD64 Rbx;
    PDWORD64 Rsp;
    PDWORD64 Rbp;
    PDWORD64 Rsi;
    PDWORD64 Rdi;
    PDWORD64 R8;
    PDWORD64 R9;
    PDWORD64 R10;
    PDWORD64 R11;
    PDWORD64 R12;
    PDWORD64 R13;
    PDWORD64 R14;
    PDWORD64 R15;
};

union _union_63 {
    PDWORD64 IntegerContext[16];
    struct _struct_64 s;
};

typedef EXCEPTION_DISPOSITION (EXCEPTION_ROUTINE)(struct _EXCEPTION_RECORD *, PVOID, struct _CONTEXT *, PVOID);

typedef WCHAR *PWSTR;

typedef struct _OSVERSIONINFOEXA _OSVERSIONINFOEXA, *P_OSVERSIONINFOEXA;

struct _OSVERSIONINFOEXA {
    DWORD dwOSVersionInfoSize;
    DWORD dwMajorVersion;
    DWORD dwMinorVersion;
    DWORD dwBuildNumber;
    DWORD dwPlatformId;
    CHAR szCSDVersion[128];
    WORD wServicePackMajor;
    WORD wServicePackMinor;
    WORD wSuiteMask;
    BYTE wProductType;
    BYTE wReserved;
};

typedef struct _LUID *PLUID;

typedef struct _OSVERSIONINFOW _OSVERSIONINFOW, *P_OSVERSIONINFOW;

typedef struct _OSVERSIONINFOW *LPOSVERSIONINFOW;

struct _OSVERSIONINFOW {
    DWORD dwOSVersionInfoSize;
    DWORD dwMajorVersion;
    DWORD dwMinorVersion;
    DWORD dwBuildNumber;
    DWORD dwPlatformId;
    WCHAR szCSDVersion[128];
};

typedef CHAR *LPCSTR;

typedef LONG *PLONG;

typedef ULARGE_INTEGER *PULARGE_INTEGER;

typedef struct _OSVERSIONINFOA _OSVERSIONINFOA, *P_OSVERSIONINFOA;

typedef struct _OSVERSIONINFOA *LPOSVERSIONINFOA;

struct _OSVERSIONINFOA {
    DWORD dwOSVersionInfoSize;
    DWORD dwMajorVersion;
    DWORD dwMinorVersion;
    DWORD dwBuildNumber;
    DWORD dwPlatformId;
    CHAR szCSDVersion[128];
};

typedef DWORD EXECUTION_STATE;

typedef struct _TOKEN_PRIVILEGES *PTOKEN_PRIVILEGES;

typedef DWORD ACCESS_MASK;

typedef union _union_238 _union_238, *P_union_238;

union _union_238 {
    DWORD PhysicalAddress;
    DWORD VirtualSize;
};

typedef struct _OSVERSIONINFOEXW _OSVERSIONINFOEXW, *P_OSVERSIONINFOEXW;

struct _OSVERSIONINFOEXW {
    DWORD dwOSVersionInfoSize;
    DWORD dwMajorVersion;
    DWORD dwMinorVersion;
    DWORD dwBuildNumber;
    DWORD dwPlatformId;
    WCHAR szCSDVersion[128];
    WORD wServicePackMajor;
    WORD wServicePackMinor;
    WORD wSuiteMask;
    BYTE wProductType;
    BYTE wReserved;
};

typedef union _LARGE_INTEGER _LARGE_INTEGER, *P_LARGE_INTEGER;

typedef union _LARGE_INTEGER LARGE_INTEGER;

typedef struct _struct_19 _struct_19, *P_struct_19;

typedef struct _struct_20 _struct_20, *P_struct_20;

struct _struct_20 {
    DWORD LowPart;
    LONG HighPart;
};

struct _struct_19 {
    DWORD LowPart;
    LONG HighPart;
};

union _LARGE_INTEGER {
    struct _struct_19 s;
    struct _struct_20 u;
    LONGLONG QuadPart;
};

typedef WCHAR *PCWSTR;

typedef struct _IMAGE_SECTION_HEADER _IMAGE_SECTION_HEADER, *P_IMAGE_SECTION_HEADER;

typedef struct _IMAGE_SECTION_HEADER *PIMAGE_SECTION_HEADER;

struct _IMAGE_SECTION_HEADER {
    BYTE Name[8];
    union _union_238 Misc;
    DWORD VirtualAddress;
    DWORD SizeOfRawData;
    DWORD PointerToRawData;
    DWORD PointerToRelocations;
    DWORD PointerToLinenumbers;
    WORD NumberOfRelocations;
    WORD NumberOfLinenumbers;
    DWORD Characteristics;
};

typedef WCHAR *LPWCH;

typedef BYTE BOOLEAN;

typedef EXCEPTION_ROUTINE *PEXCEPTION_ROUTINE;

typedef short SHORT;

typedef DWORD LCID;

typedef HANDLE *PHANDLE;

typedef WCHAR *PCNZWCH;

typedef struct _UNWIND_HISTORY_TABLE _UNWIND_HISTORY_TABLE, *P_UNWIND_HISTORY_TABLE;

struct _UNWIND_HISTORY_TABLE {
    DWORD Count;
    BYTE LocalHint;
    BYTE GlobalHint;
    BYTE Search;
    BYTE Once;
    DWORD64 LowAddress;
    DWORD64 HighAddress;
    UNWIND_HISTORY_TABLE_ENTRY Entry[12];
};

typedef void (*PAPCFUNC)(ULONG_PTR);

typedef struct _MEMORY_BASIC_INFORMATION _MEMORY_BASIC_INFORMATION, *P_MEMORY_BASIC_INFORMATION;

typedef struct _MEMORY_BASIC_INFORMATION *PMEMORY_BASIC_INFORMATION;

struct _MEMORY_BASIC_INFORMATION {
    PVOID BaseAddress;
    PVOID AllocationBase;
    DWORD AllocationProtect;
    SIZE_T RegionSize;
    DWORD State;
    DWORD Protect;
    DWORD Type;
};

typedef struct _KNONVOLATILE_CONTEXT_POINTERS _KNONVOLATILE_CONTEXT_POINTERS, *P_KNONVOLATILE_CONTEXT_POINTERS;

struct _KNONVOLATILE_CONTEXT_POINTERS {
    union _union_61 u;
    union _union_63 u2;
};

typedef struct _OSVERSIONINFOEXW *LPOSVERSIONINFOEXW;

typedef LONG (*PVECTORED_EXCEPTION_HANDLER)(struct _EXCEPTION_POINTERS *);

typedef struct _UNWIND_HISTORY_TABLE *PUNWIND_HISTORY_TABLE;

typedef LARGE_INTEGER *PLARGE_INTEGER;

typedef struct _KNONVOLATILE_CONTEXT_POINTERS *PKNONVOLATILE_CONTEXT_POINTERS;

typedef CHAR *PSTR;

typedef struct _OSVERSIONINFOEXA *LPOSVERSIONINFOEXA;

typedef CHAR *PCNZCH;

typedef ULONG_PTR HCRYPTKEY;

typedef struct _CERT_REVOCATION_CRL_INFO _CERT_REVOCATION_CRL_INFO, *P_CERT_REVOCATION_CRL_INFO;

typedef struct _CRL_CONTEXT _CRL_CONTEXT, *P_CRL_CONTEXT;

typedef struct _CRL_CONTEXT CRL_CONTEXT;

typedef CRL_CONTEXT *PCCRL_CONTEXT;

typedef struct _CRL_ENTRY _CRL_ENTRY, *P_CRL_ENTRY;

typedef struct _CRL_ENTRY *PCRL_ENTRY;

typedef struct _CRL_INFO _CRL_INFO, *P_CRL_INFO;

typedef struct _CRL_INFO *PCRL_INFO;

typedef void *HCERTSTORE;

typedef struct _CRYPTOAPI_BLOB _CRYPTOAPI_BLOB, *P_CRYPTOAPI_BLOB;

typedef struct _CRYPTOAPI_BLOB CRYPT_INTEGER_BLOB;

typedef struct _CERT_EXTENSION _CERT_EXTENSION, *P_CERT_EXTENSION;

typedef struct _CERT_EXTENSION *PCERT_EXTENSION;

typedef struct _CRYPT_ALGORITHM_IDENTIFIER _CRYPT_ALGORITHM_IDENTIFIER, *P_CRYPT_ALGORITHM_IDENTIFIER;

typedef struct _CRYPT_ALGORITHM_IDENTIFIER CRYPT_ALGORITHM_IDENTIFIER;

typedef struct _CRYPTOAPI_BLOB CERT_NAME_BLOB;

typedef struct _CRYPTOAPI_BLOB CRYPT_OBJID_BLOB;

struct _CRYPTOAPI_BLOB {
    DWORD cbData;
    BYTE *pbData;
};

struct _CRL_ENTRY {
    CRYPT_INTEGER_BLOB SerialNumber;
    FILETIME RevocationDate;
    DWORD cExtension;
    PCERT_EXTENSION rgExtension;
};

struct _CERT_EXTENSION {
    LPSTR pszObjId;
    BOOL fCritical;
    CRYPT_OBJID_BLOB Value;
};

struct _CRYPT_ALGORITHM_IDENTIFIER {
    LPSTR pszObjId;
    CRYPT_OBJID_BLOB Parameters;
};

struct _CERT_REVOCATION_CRL_INFO {
    DWORD cbSize;
    PCCRL_CONTEXT pBaseCrlContext;
    PCCRL_CONTEXT pDeltaCrlContext;
    PCRL_ENTRY pCrlEntry;
    BOOL fDeltaCrlEntry;
};

struct _CRL_CONTEXT {
    DWORD dwCertEncodingType;
    BYTE *pbCrlEncoded;
    DWORD cbCrlEncoded;
    PCRL_INFO pCrlInfo;
    HCERTSTORE hCertStore;
};

struct _CRL_INFO {
    DWORD dwVersion;
    CRYPT_ALGORITHM_IDENTIFIER SignatureAlgorithm;
    CERT_NAME_BLOB Issuer;
    FILETIME ThisUpdate;
    FILETIME NextUpdate;
    DWORD cCRLEntry;
    PCRL_ENTRY rgCRLEntry;
    DWORD cExtension;
    PCERT_EXTENSION rgExtension;
};

typedef struct _CRYPT_BIT_BLOB _CRYPT_BIT_BLOB, *P_CRYPT_BIT_BLOB;

struct _CRYPT_BIT_BLOB {
    DWORD cbData;
    BYTE *pbData;
    DWORD cUnusedBits;
};

typedef ULONG_PTR HCRYPTHASH;

typedef struct _CERT_PUBLIC_KEY_INFO _CERT_PUBLIC_KEY_INFO, *P_CERT_PUBLIC_KEY_INFO;

typedef struct _CERT_PUBLIC_KEY_INFO CERT_PUBLIC_KEY_INFO;

typedef struct _CRYPT_BIT_BLOB CRYPT_BIT_BLOB;

struct _CERT_PUBLIC_KEY_INFO {
    CRYPT_ALGORITHM_IDENTIFIER Algorithm;
    CRYPT_BIT_BLOB PublicKey;
};

typedef struct _CERT_CONTEXT _CERT_CONTEXT, *P_CERT_CONTEXT;

typedef struct _CERT_CONTEXT CERT_CONTEXT;

typedef struct _CERT_INFO _CERT_INFO, *P_CERT_INFO;

typedef struct _CERT_INFO *PCERT_INFO;

struct _CERT_INFO {
    DWORD dwVersion;
    CRYPT_INTEGER_BLOB SerialNumber;
    CRYPT_ALGORITHM_IDENTIFIER SignatureAlgorithm;
    CERT_NAME_BLOB Issuer;
    FILETIME NotBefore;
    FILETIME NotAfter;
    CERT_NAME_BLOB Subject;
    CERT_PUBLIC_KEY_INFO SubjectPublicKeyInfo;
    CRYPT_BIT_BLOB IssuerUniqueId;
    CRYPT_BIT_BLOB SubjectUniqueId;
    DWORD cExtension;
    PCERT_EXTENSION rgExtension;
};

struct _CERT_CONTEXT {
    DWORD dwCertEncodingType;
    BYTE *pbCertEncoded;
    DWORD cbCertEncoded;
    PCERT_INFO pCertInfo;
    HCERTSTORE hCertStore;
};

typedef struct _CERT_CHAIN_CONTEXT _CERT_CHAIN_CONTEXT, *P_CERT_CHAIN_CONTEXT;

typedef struct _CERT_CHAIN_CONTEXT CERT_CHAIN_CONTEXT;

typedef CERT_CHAIN_CONTEXT *PCCERT_CHAIN_CONTEXT;

typedef struct _CERT_TRUST_STATUS _CERT_TRUST_STATUS, *P_CERT_TRUST_STATUS;

typedef struct _CERT_TRUST_STATUS CERT_TRUST_STATUS;

typedef struct _CERT_SIMPLE_CHAIN _CERT_SIMPLE_CHAIN, *P_CERT_SIMPLE_CHAIN;

typedef struct _CERT_SIMPLE_CHAIN *PCERT_SIMPLE_CHAIN;

typedef struct _CERT_CHAIN_ELEMENT _CERT_CHAIN_ELEMENT, *P_CERT_CHAIN_ELEMENT;

typedef struct _CERT_CHAIN_ELEMENT *PCERT_CHAIN_ELEMENT;

typedef struct _CERT_TRUST_LIST_INFO _CERT_TRUST_LIST_INFO, *P_CERT_TRUST_LIST_INFO;

typedef struct _CERT_TRUST_LIST_INFO *PCERT_TRUST_LIST_INFO;

typedef CERT_CONTEXT *PCCERT_CONTEXT;

typedef struct _CERT_REVOCATION_INFO _CERT_REVOCATION_INFO, *P_CERT_REVOCATION_INFO;

typedef struct _CERT_REVOCATION_INFO *PCERT_REVOCATION_INFO;

typedef struct _CTL_USAGE _CTL_USAGE, *P_CTL_USAGE;

typedef struct _CTL_USAGE *PCERT_ENHKEY_USAGE;

typedef struct _CTL_ENTRY _CTL_ENTRY, *P_CTL_ENTRY;

typedef struct _CTL_ENTRY *PCTL_ENTRY;

typedef struct _CTL_CONTEXT _CTL_CONTEXT, *P_CTL_CONTEXT;

typedef struct _CTL_CONTEXT CTL_CONTEXT;

typedef CTL_CONTEXT *PCCTL_CONTEXT;

typedef struct _CERT_REVOCATION_CRL_INFO *PCERT_REVOCATION_CRL_INFO;

typedef struct _CRYPTOAPI_BLOB CRYPT_DATA_BLOB;

typedef struct _CRYPT_ATTRIBUTE _CRYPT_ATTRIBUTE, *P_CRYPT_ATTRIBUTE;

typedef struct _CRYPT_ATTRIBUTE *PCRYPT_ATTRIBUTE;

typedef struct _CTL_INFO _CTL_INFO, *P_CTL_INFO;

typedef struct _CTL_INFO *PCTL_INFO;

typedef void *HCRYPTMSG;

typedef struct _CRYPTOAPI_BLOB *PCRYPT_ATTR_BLOB;

typedef struct _CTL_USAGE CTL_USAGE;

struct _CERT_TRUST_STATUS {
    DWORD dwErrorStatus;
    DWORD dwInfoStatus;
};

struct _CERT_CHAIN_ELEMENT {
    DWORD cbSize;
    PCCERT_CONTEXT pCertContext;
    CERT_TRUST_STATUS TrustStatus;
    PCERT_REVOCATION_INFO pRevocationInfo;
    PCERT_ENHKEY_USAGE pIssuanceUsage;
    PCERT_ENHKEY_USAGE pApplicationUsage;
    LPCWSTR pwszExtendedErrorInfo;
};

struct _CERT_CHAIN_CONTEXT {
    DWORD cbSize;
    CERT_TRUST_STATUS TrustStatus;
    DWORD cChain;
    PCERT_SIMPLE_CHAIN *rgpChain;
    DWORD cLowerQualityChainContext;
    PCCERT_CHAIN_CONTEXT *rgpLowerQualityChainContext;
    BOOL fHasRevocationFreshnessTime;
    DWORD dwRevocationFreshnessTime;
    DWORD dwCreateFlags;
    GUID ChainId;
};

struct _CERT_SIMPLE_CHAIN {
    DWORD cbSize;
    CERT_TRUST_STATUS TrustStatus;
    DWORD cElement;
    PCERT_CHAIN_ELEMENT *rgpElement;
    PCERT_TRUST_LIST_INFO pTrustListInfo;
    BOOL fHasRevocationFreshnessTime;
    DWORD dwRevocationFreshnessTime;
};

struct _CERT_REVOCATION_INFO {
    DWORD cbSize;
    DWORD dwRevocationResult;
    LPCSTR pszRevocationOid;
    LPVOID pvOidSpecificInfo;
    BOOL fHasFreshnessTime;
    DWORD dwFreshnessTime;
    PCERT_REVOCATION_CRL_INFO pCrlInfo;
};

struct _CTL_USAGE {
    DWORD cUsageIdentifier;
    LPSTR *rgpszUsageIdentifier;
};

struct _CRYPT_ATTRIBUTE {
    LPSTR pszObjId;
    DWORD cValue;
    PCRYPT_ATTR_BLOB rgValue;
};

struct _CTL_ENTRY {
    CRYPT_DATA_BLOB SubjectIdentifier;
    DWORD cAttribute;
    PCRYPT_ATTRIBUTE rgAttribute;
};

struct _CTL_INFO {
    DWORD dwVersion;
    CTL_USAGE SubjectUsage;
    CRYPT_DATA_BLOB ListIdentifier;
    CRYPT_INTEGER_BLOB SequenceNumber;
    FILETIME ThisUpdate;
    FILETIME NextUpdate;
    CRYPT_ALGORITHM_IDENTIFIER SubjectAlgorithm;
    DWORD cCTLEntry;
    PCTL_ENTRY rgCTLEntry;
    DWORD cExtension;
    PCERT_EXTENSION rgExtension;
};

struct _CERT_TRUST_LIST_INFO {
    DWORD cbSize;
    PCTL_ENTRY pCtlEntry;
    PCCTL_CONTEXT pCtlContext;
};

struct _CTL_CONTEXT {
    DWORD dwMsgAndCertEncodingType;
    BYTE *pbCtlEncoded;
    DWORD cbCtlEncoded;
    PCTL_INFO pCtlInfo;
    HCERTSTORE hCertStore;
    HCRYPTMSG hCryptMsg;
    BYTE *pbCtlContent;
    DWORD cbCtlContent;
};

typedef struct _CERT_CHAIN_POLICY_STATUS _CERT_CHAIN_POLICY_STATUS, *P_CERT_CHAIN_POLICY_STATUS;

typedef struct _CERT_CHAIN_POLICY_STATUS *PCERT_CHAIN_POLICY_STATUS;

struct _CERT_CHAIN_POLICY_STATUS {
    DWORD cbSize;
    DWORD dwError;
    LONG lChainIndex;
    LONG lElementIndex;
    void *pvExtraPolicyStatus;
};

typedef struct _CERT_USAGE_MATCH _CERT_USAGE_MATCH, *P_CERT_USAGE_MATCH;

typedef struct _CTL_USAGE CERT_ENHKEY_USAGE;

struct _CERT_USAGE_MATCH {
    DWORD dwType;
    CERT_ENHKEY_USAGE Usage;
};

typedef struct _CERT_CHAIN_ENGINE_CONFIG _CERT_CHAIN_ENGINE_CONFIG, *P_CERT_CHAIN_ENGINE_CONFIG;

typedef struct _CERT_CHAIN_ENGINE_CONFIG *PCERT_CHAIN_ENGINE_CONFIG;

struct _CERT_CHAIN_ENGINE_CONFIG {
    DWORD cbSize;
    HCERTSTORE hRestrictedRoot;
    HCERTSTORE hRestrictedTrust;
    HCERTSTORE hRestrictedOther;
    DWORD cAdditionalStore;
    HCERTSTORE *rghAdditionalStore;
    DWORD dwFlags;
    DWORD dwUrlRetrievalTimeout;
    DWORD MaximumCachedCertificates;
    DWORD CycleDetectionModulus;
};

typedef ULONG_PTR HCRYPTPROV;

typedef struct _CRYPT_DECODE_PARA _CRYPT_DECODE_PARA, *P_CRYPT_DECODE_PARA;

typedef LPVOID (*PFN_CRYPT_ALLOC)(size_t);

typedef void (*PFN_CRYPT_FREE)(LPVOID);

struct _CRYPT_DECODE_PARA {
    DWORD cbSize;
    PFN_CRYPT_ALLOC pfnAlloc;
    PFN_CRYPT_FREE pfnFree;
};

typedef struct _CERT_USAGE_MATCH CERT_USAGE_MATCH;

typedef HANDLE HCERTCHAINENGINE;

typedef struct _CRYPTPROTECT_PROMPTSTRUCT _CRYPTPROTECT_PROMPTSTRUCT, *P_CRYPTPROTECT_PROMPTSTRUCT;

typedef struct _CRYPTPROTECT_PROMPTSTRUCT CRYPTPROTECT_PROMPTSTRUCT;

struct _CRYPTPROTECT_PROMPTSTRUCT {
    DWORD cbSize;
    DWORD dwPromptFlags;
    HWND hwndApp;
    LPCWSTR szPrompt;
};

typedef struct _CERT_EXTENSION CERT_EXTENSION;

typedef struct _CRYPTOAPI_BLOB DATA_BLOB;

typedef ULONG_PTR HCRYPTPROV_LEGACY;

typedef struct _CERT_CHAIN_POLICY_PARA _CERT_CHAIN_POLICY_PARA, *P_CERT_CHAIN_POLICY_PARA;

struct _CERT_CHAIN_POLICY_PARA {
    DWORD cbSize;
    DWORD dwFlags;
    void *pvExtraPolicyPara;
};

typedef struct _CERT_CHAIN_POLICY_PARA *PCERT_CHAIN_POLICY_PARA;

typedef struct _CERT_CHAIN_PARA _CERT_CHAIN_PARA, *P_CERT_CHAIN_PARA;

struct _CERT_CHAIN_PARA {
    DWORD cbSize;
    CERT_USAGE_MATCH RequestedUsage;
};

typedef uint ALG_ID;

typedef struct _CRYPT_DECODE_PARA *PCRYPT_DECODE_PARA;

typedef struct _CRYPTOAPI_BLOB *PCERT_NAME_BLOB;

typedef struct _CERT_CHAIN_PARA *PCERT_CHAIN_PARA;

typedef struct tm tm, *Ptm;

struct tm {
    int tm_sec;
    int tm_min;
    int tm_hour;
    int tm_mday;
    int tm_mon;
    int tm_year;
    int tm_wday;
    int tm_yday;
    int tm_isdst;
};

typedef long clock_t;

typedef struct HKL__ HKL__, *PHKL__;

struct HKL__ {
    int unused;
};

typedef struct HKEY__ HKEY__, *PHKEY__;

struct HKEY__ {
    int unused;
};

typedef long *LPLONG;

typedef INT_PTR (*FARPROC)(void);

typedef BOOL *LPBOOL;

typedef struct HKEY__ *HKEY;

typedef DWORD *LPDWORD;

typedef struct HHOOK__ HHOOK__, *PHHOOK__;

struct HHOOK__ {
    int unused;
};

typedef DWORD *PDWORD;

typedef struct _FILETIME *PFILETIME;

typedef uchar UCHAR;

typedef WORD *LPWORD;

typedef struct tagPOINT *LPPOINT;

typedef RECT *LPCRECT;

typedef uint *PUINT;

typedef HANDLE HLOCAL;

typedef WORD ATOM;

typedef void *HGDIOBJ;

typedef struct HHOOK__ *HHOOK;

typedef DWORD COLORREF;

typedef UCHAR *PUCHAR;

typedef struct HKL__ *HKL;

typedef struct HMENU__ HMENU__, *PHMENU__;

typedef struct HMENU__ *HMENU;

struct HMENU__ {
    int unused;
};

typedef struct _FILETIME *LPFILETIME;

typedef HANDLE *LPHANDLE;

typedef HKEY *PHKEY;

typedef int INT;

typedef HANDLE HGLOBAL;

typedef BYTE *PBYTE;

typedef void *LPCVOID;

typedef struct Var Var, *PVar;

struct Var {
    word wLength;
    word wValueLength;
    word wType;
};

typedef struct IMAGE_RESOURCE_DIRECTORY_ENTRY_NameStruct IMAGE_RESOURCE_DIRECTORY_ENTRY_NameStruct, *PIMAGE_RESOURCE_DIRECTORY_ENTRY_NameStruct;

struct IMAGE_RESOURCE_DIRECTORY_ENTRY_NameStruct {
    dword NameOffset:31;
    dword NameIsString:1;
};

typedef struct IMAGE_DEBUG_DIRECTORY IMAGE_DEBUG_DIRECTORY, *PIMAGE_DEBUG_DIRECTORY;

struct IMAGE_DEBUG_DIRECTORY {
    dword Characteristics;
    dword TimeDateStamp;
    word MajorVersion;
    word MinorVersion;
    dword Type;
    dword SizeOfData;
    dword AddressOfRawData;
    dword PointerToRawData;
};

typedef struct StringTable StringTable, *PStringTable;

struct StringTable {
    word wLength;
    word wValueLength;
    word wType;
};

typedef struct IMAGE_SECTION_HEADER IMAGE_SECTION_HEADER, *PIMAGE_SECTION_HEADER;

typedef union Misc Misc, *PMisc;

typedef enum SectionFlags {
    IMAGE_SCN_TYPE_NO_PAD=8,
    IMAGE_SCN_RESERVED_0001=16,
    IMAGE_SCN_CNT_CODE=32,
    IMAGE_SCN_CNT_INITIALIZED_DATA=64,
    IMAGE_SCN_CNT_UNINITIALIZED_DATA=128,
    IMAGE_SCN_LNK_OTHER=256,
    IMAGE_SCN_LNK_INFO=512,
    IMAGE_SCN_RESERVED_0040=1024,
    IMAGE_SCN_LNK_REMOVE=2048,
    IMAGE_SCN_LNK_COMDAT=4096,
    IMAGE_SCN_GPREL=32768,
    IMAGE_SCN_MEM_16BIT=131072,
    IMAGE_SCN_MEM_PURGEABLE=131072,
    IMAGE_SCN_MEM_LOCKED=262144,
    IMAGE_SCN_MEM_PRELOAD=524288,
    IMAGE_SCN_ALIGN_1BYTES=1048576,
    IMAGE_SCN_ALIGN_2BYTES=2097152,
    IMAGE_SCN_ALIGN_4BYTES=3145728,
    IMAGE_SCN_ALIGN_8BYTES=4194304,
    IMAGE_SCN_ALIGN_16BYTES=5242880,
    IMAGE_SCN_ALIGN_32BYTES=6291456,
    IMAGE_SCN_ALIGN_64BYTES=7340032,
    IMAGE_SCN_ALIGN_128BYTES=8388608,
    IMAGE_SCN_ALIGN_256BYTES=9437184,
    IMAGE_SCN_ALIGN_512BYTES=10485760,
    IMAGE_SCN_ALIGN_1024BYTES=11534336,
    IMAGE_SCN_ALIGN_2048BYTES=12582912,
    IMAGE_SCN_ALIGN_4096BYTES=13631488,
    IMAGE_SCN_ALIGN_8192BYTES=14680064,
    IMAGE_SCN_LNK_NRELOC_OVFL=16777216,
    IMAGE_SCN_MEM_DISCARDABLE=33554432,
    IMAGE_SCN_MEM_NOT_CACHED=67108864,
    IMAGE_SCN_MEM_NOT_PAGED=134217728,
    IMAGE_SCN_MEM_SHARED=268435456,
    IMAGE_SCN_MEM_EXECUTE=536870912,
    IMAGE_SCN_MEM_READ=1073741824,
    IMAGE_SCN_MEM_WRITE=2147483648
} SectionFlags;

union Misc {
    dword PhysicalAddress;
    dword VirtualSize;
};

struct IMAGE_SECTION_HEADER {
    char Name[8];
    union Misc Misc;
    ImageBaseOffset32 VirtualAddress;
    dword SizeOfRawData;
    dword PointerToRawData;
    dword PointerToRelocations;
    dword PointerToLinenumbers;
    word NumberOfRelocations;
    word NumberOfLinenumbers;
    enum SectionFlags Characteristics;
};

typedef struct IMAGE_NT_HEADERS64 IMAGE_NT_HEADERS64, *PIMAGE_NT_HEADERS64;

typedef struct IMAGE_FILE_HEADER IMAGE_FILE_HEADER, *PIMAGE_FILE_HEADER;

typedef struct IMAGE_OPTIONAL_HEADER64 IMAGE_OPTIONAL_HEADER64, *PIMAGE_OPTIONAL_HEADER64;

typedef struct IMAGE_DATA_DIRECTORY IMAGE_DATA_DIRECTORY, *PIMAGE_DATA_DIRECTORY;

struct IMAGE_DATA_DIRECTORY {
    ImageBaseOffset32 VirtualAddress;
    dword Size;
};

struct IMAGE_OPTIONAL_HEADER64 {
    word Magic;
    byte MajorLinkerVersion;
    byte MinorLinkerVersion;
    dword SizeOfCode;
    dword SizeOfInitializedData;
    dword SizeOfUninitializedData;
    ImageBaseOffset32 AddressOfEntryPoint;
    ImageBaseOffset32 BaseOfCode;
    pointer64 ImageBase;
    dword SectionAlignment;
    dword FileAlignment;
    word MajorOperatingSystemVersion;
    word MinorOperatingSystemVersion;
    word MajorImageVersion;
    word MinorImageVersion;
    word MajorSubsystemVersion;
    word MinorSubsystemVersion;
    dword Win32VersionValue;
    dword SizeOfImage;
    dword SizeOfHeaders;
    dword CheckSum;
    word Subsystem;
    word DllCharacteristics;
    qword SizeOfStackReserve;
    qword SizeOfStackCommit;
    qword SizeOfHeapReserve;
    qword SizeOfHeapCommit;
    dword LoaderFlags;
    dword NumberOfRvaAndSizes;
    struct IMAGE_DATA_DIRECTORY DataDirectory[16];
};

struct IMAGE_FILE_HEADER {
    word Machine; /* 34404 */
    word NumberOfSections;
    dword TimeDateStamp;
    dword PointerToSymbolTable;
    dword NumberOfSymbols;
    word SizeOfOptionalHeader;
    word Characteristics;
};

struct IMAGE_NT_HEADERS64 {
    char Signature[4];
    struct IMAGE_FILE_HEADER FileHeader;
    struct IMAGE_OPTIONAL_HEADER64 OptionalHeader;
};

typedef struct IMAGE_RESOURCE_DATA_ENTRY IMAGE_RESOURCE_DATA_ENTRY, *PIMAGE_RESOURCE_DATA_ENTRY;

struct IMAGE_RESOURCE_DATA_ENTRY {
    dword OffsetToData;
    dword Size;
    dword CodePage;
    dword Reserved;
};

typedef struct IMAGE_RESOURCE_DIRECTORY IMAGE_RESOURCE_DIRECTORY, *PIMAGE_RESOURCE_DIRECTORY;

struct IMAGE_RESOURCE_DIRECTORY {
    dword Characteristics;
    dword TimeDateStamp;
    word MajorVersion;
    word MinorVersion;
    word NumberOfNamedEntries;
    word NumberOfIdEntries;
};

typedef struct IMAGE_DIRECTORY_ENTRY_EXPORT IMAGE_DIRECTORY_ENTRY_EXPORT, *PIMAGE_DIRECTORY_ENTRY_EXPORT;

struct IMAGE_DIRECTORY_ENTRY_EXPORT {
    dword Characteristics;
    dword TimeDateStamp;
    word MajorVersion;
    word MinorVersion;
    ImageBaseOffset32 Name;
    dword Base;
    dword NumberOfFunctions;
    dword NumberOfNames;
    ImageBaseOffset32 AddressOfFunctions;
    ImageBaseOffset32 AddressOfNames;
    ImageBaseOffset32 AddressOfNameOrdinals;
};

typedef union IMAGE_RESOURCE_DIRECTORY_ENTRY_NameUnion IMAGE_RESOURCE_DIRECTORY_ENTRY_NameUnion, *PIMAGE_RESOURCE_DIRECTORY_ENTRY_NameUnion;

union IMAGE_RESOURCE_DIRECTORY_ENTRY_NameUnion {
    struct IMAGE_RESOURCE_DIRECTORY_ENTRY_NameStruct IMAGE_RESOURCE_DIRECTORY_ENTRY_NameStruct;
    dword Name;
    word Id;
};

typedef struct _IMAGE_RUNTIME_FUNCTION_ENTRY _IMAGE_RUNTIME_FUNCTION_ENTRY, *P_IMAGE_RUNTIME_FUNCTION_ENTRY;

struct _IMAGE_RUNTIME_FUNCTION_ENTRY {
    ImageBaseOffset32 BeginAddress;
    dword EndAddress; /* Apply ImageBaseOffset32 to see reference */
    ImageBaseOffset32 UnwindInfoAddressOrData;
};

typedef struct StringFileInfo StringFileInfo, *PStringFileInfo;

struct StringFileInfo {
    word wLength;
    word wValueLength;
    word wType;
};

typedef struct IMAGE_RESOURCE_DIRECTORY_ENTRY IMAGE_RESOURCE_DIRECTORY_ENTRY, *PIMAGE_RESOURCE_DIRECTORY_ENTRY;

struct IMAGE_RESOURCE_DIRECTORY_ENTRY {
    union IMAGE_RESOURCE_DIRECTORY_ENTRY_NameUnion NameUnion;
    union IMAGE_RESOURCE_DIRECTORY_ENTRY_DirectoryUnion DirectoryUnion;
};

typedef struct VS_VERSION_INFO VS_VERSION_INFO, *PVS_VERSION_INFO;

struct VS_VERSION_INFO {
    word StructLength;
    word ValueLength;
    word StructType;
    wchar16 Info[16];
    byte Padding[2];
    dword Signature;
    word StructVersion[2];
    word FileVersion[4];
    word ProductVersion[4];
    dword FileFlagsMask[2];
    dword FileFlags;
    dword FileOS;
    dword FileType;
    dword FileSubtype;
    dword FileTimestamp;
};

typedef struct IMAGE_BASE_RELOCATION IMAGE_BASE_RELOCATION, *PIMAGE_BASE_RELOCATION;

struct IMAGE_BASE_RELOCATION {
    dword VirtualAddress;
    dword SizeOfBlock;
};

typedef struct IMAGE_THUNK_DATA64 IMAGE_THUNK_DATA64, *PIMAGE_THUNK_DATA64;

struct IMAGE_THUNK_DATA64 {
    qword StartAddressOfRawData;
    qword EndAddressOfRawData;
    qword AddressOfIndex;
    qword AddressOfCallBacks;
    dword SizeOfZeroFill;
    dword Characteristics;
};

typedef struct VarFileInfo VarFileInfo, *PVarFileInfo;

struct VarFileInfo {
    word wLength;
    word wValueLength;
    word wType;
};

typedef struct StringInfo StringInfo, *PStringInfo;

struct StringInfo {
    word wLength;
    word wValueLength;
    word wType;
};

typedef ACCESS_MASK REGSAM;

typedef LONG LSTATUS;

typedef struct tagPROPVARIANT tagPROPVARIANT, *PtagPROPVARIANT;

typedef struct tagPROPVARIANT PROPVARIANT;

struct tagPROPVARIANT {
};

typedef struct tagCANDIDATELIST tagCANDIDATELIST, *PtagCANDIDATELIST;

typedef struct tagCANDIDATELIST *LPCANDIDATELIST;

struct tagCANDIDATELIST {
    DWORD dwSize;
    DWORD dwStyle;
    DWORD dwCount;
    DWORD dwSelection;
    DWORD dwPageStart;
    DWORD dwPageSize;
    DWORD dwOffset[1];
};

typedef struct HIMC__ HIMC__, *PHIMC__;

struct HIMC__ {
    int unused;
};

typedef struct HIMC__ *HIMC;

typedef struct _NOTIFYICONDATAA _NOTIFYICONDATAA, *P_NOTIFYICONDATAA;

struct _NOTIFYICONDATAA {
    DWORD cbSize;
    HWND hWnd;
    UINT uID;
    UINT uFlags;
    UINT uCallbackMessage;
    HICON hIcon;
    CHAR szTip[64];
};

typedef struct _NOTIFYICONDATAA *PNOTIFYICONDATAA;

typedef struct IUnknownVtbl IUnknownVtbl, *PIUnknownVtbl;

typedef struct IUnknown IUnknown, *PIUnknown;

struct IUnknownVtbl {
    HRESULT (*QueryInterface)(struct IUnknown *, IID *, void **);
    ULONG (*AddRef)(struct IUnknown *);
    ULONG (*Release)(struct IUnknown *);
};

struct IUnknown {
    struct IUnknownVtbl *lpVtbl;
};

typedef struct IUnknown *LPUNKNOWN;

