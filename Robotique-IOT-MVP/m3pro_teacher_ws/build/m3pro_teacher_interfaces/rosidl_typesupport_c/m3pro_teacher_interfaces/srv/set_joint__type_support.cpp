// generated from rosidl_typesupport_c/resource/idl__type_support.cpp.em
// with input from m3pro_teacher_interfaces:srv/SetJoint.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "m3pro_teacher_interfaces/srv/detail/set_joint__struct.h"
#include "m3pro_teacher_interfaces/srv/detail/set_joint__type_support.h"
#include "rosidl_typesupport_c/identifier.h"
#include "rosidl_typesupport_c/message_type_support_dispatch.h"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_c/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace m3pro_teacher_interfaces
{

namespace srv
{

namespace rosidl_typesupport_c
{

typedef struct _SetJoint_Request_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _SetJoint_Request_type_support_ids_t;

static const _SetJoint_Request_type_support_ids_t _SetJoint_Request_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _SetJoint_Request_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _SetJoint_Request_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _SetJoint_Request_type_support_symbol_names_t _SetJoint_Request_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, m3pro_teacher_interfaces, srv, SetJoint_Request)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, m3pro_teacher_interfaces, srv, SetJoint_Request)),
  }
};

typedef struct _SetJoint_Request_type_support_data_t
{
  void * data[2];
} _SetJoint_Request_type_support_data_t;

static _SetJoint_Request_type_support_data_t _SetJoint_Request_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _SetJoint_Request_message_typesupport_map = {
  2,
  "m3pro_teacher_interfaces",
  &_SetJoint_Request_message_typesupport_ids.typesupport_identifier[0],
  &_SetJoint_Request_message_typesupport_symbol_names.symbol_name[0],
  &_SetJoint_Request_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t SetJoint_Request_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_SetJoint_Request_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace srv

}  // namespace m3pro_teacher_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, m3pro_teacher_interfaces, srv, SetJoint_Request)() {
  return &::m3pro_teacher_interfaces::srv::rosidl_typesupport_c::SetJoint_Request_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "m3pro_teacher_interfaces/srv/detail/set_joint__struct.h"
// already included above
// #include "m3pro_teacher_interfaces/srv/detail/set_joint__type_support.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
// already included above
// #include "rosidl_typesupport_c/message_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_c/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace m3pro_teacher_interfaces
{

namespace srv
{

namespace rosidl_typesupport_c
{

typedef struct _SetJoint_Response_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _SetJoint_Response_type_support_ids_t;

static const _SetJoint_Response_type_support_ids_t _SetJoint_Response_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _SetJoint_Response_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _SetJoint_Response_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _SetJoint_Response_type_support_symbol_names_t _SetJoint_Response_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, m3pro_teacher_interfaces, srv, SetJoint_Response)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, m3pro_teacher_interfaces, srv, SetJoint_Response)),
  }
};

typedef struct _SetJoint_Response_type_support_data_t
{
  void * data[2];
} _SetJoint_Response_type_support_data_t;

static _SetJoint_Response_type_support_data_t _SetJoint_Response_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _SetJoint_Response_message_typesupport_map = {
  2,
  "m3pro_teacher_interfaces",
  &_SetJoint_Response_message_typesupport_ids.typesupport_identifier[0],
  &_SetJoint_Response_message_typesupport_symbol_names.symbol_name[0],
  &_SetJoint_Response_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t SetJoint_Response_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_SetJoint_Response_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace srv

}  // namespace m3pro_teacher_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, m3pro_teacher_interfaces, srv, SetJoint_Response)() {
  return &::m3pro_teacher_interfaces::srv::rosidl_typesupport_c::SetJoint_Response_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "m3pro_teacher_interfaces/srv/detail/set_joint__type_support.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
#include "rosidl_typesupport_c/service_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace m3pro_teacher_interfaces
{

namespace srv
{

namespace rosidl_typesupport_c
{

typedef struct _SetJoint_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _SetJoint_type_support_ids_t;

static const _SetJoint_type_support_ids_t _SetJoint_service_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _SetJoint_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _SetJoint_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _SetJoint_type_support_symbol_names_t _SetJoint_service_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, m3pro_teacher_interfaces, srv, SetJoint)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, m3pro_teacher_interfaces, srv, SetJoint)),
  }
};

typedef struct _SetJoint_type_support_data_t
{
  void * data[2];
} _SetJoint_type_support_data_t;

static _SetJoint_type_support_data_t _SetJoint_service_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _SetJoint_service_typesupport_map = {
  2,
  "m3pro_teacher_interfaces",
  &_SetJoint_service_typesupport_ids.typesupport_identifier[0],
  &_SetJoint_service_typesupport_symbol_names.symbol_name[0],
  &_SetJoint_service_typesupport_data.data[0],
};

static const rosidl_service_type_support_t SetJoint_service_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_SetJoint_service_typesupport_map),
  rosidl_typesupport_c__get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace srv

}  // namespace m3pro_teacher_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_c, m3pro_teacher_interfaces, srv, SetJoint)() {
  return &::m3pro_teacher_interfaces::srv::rosidl_typesupport_c::SetJoint_service_type_support_handle;
}

#ifdef __cplusplus
}
#endif
