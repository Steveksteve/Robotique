// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from m3pro_teacher_interfaces:srv/SetJoints.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "m3pro_teacher_interfaces/srv/detail/set_joints__rosidl_typesupport_introspection_c.h"
#include "m3pro_teacher_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "m3pro_teacher_interfaces/srv/detail/set_joints__functions.h"
#include "m3pro_teacher_interfaces/srv/detail/set_joints__struct.h"


// Include directives for member types
// Member `values`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__SetJoints_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  m3pro_teacher_interfaces__srv__SetJoints_Request__init(message_memory);
}

void m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__SetJoints_Request_fini_function(void * message_memory)
{
  m3pro_teacher_interfaces__srv__SetJoints_Request__fini(message_memory);
}

size_t m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__size_function__SetJoints_Request__values(
  const void * untyped_member)
{
  const rosidl_runtime_c__double__Sequence * member =
    (const rosidl_runtime_c__double__Sequence *)(untyped_member);
  return member->size;
}

const void * m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__get_const_function__SetJoints_Request__values(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__double__Sequence * member =
    (const rosidl_runtime_c__double__Sequence *)(untyped_member);
  return &member->data[index];
}

void * m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__get_function__SetJoints_Request__values(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__double__Sequence * member =
    (rosidl_runtime_c__double__Sequence *)(untyped_member);
  return &member->data[index];
}

void m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__fetch_function__SetJoints_Request__values(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const double * item =
    ((const double *)
    m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__get_const_function__SetJoints_Request__values(untyped_member, index));
  double * value =
    (double *)(untyped_value);
  *value = *item;
}

void m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__assign_function__SetJoints_Request__values(
  void * untyped_member, size_t index, const void * untyped_value)
{
  double * item =
    ((double *)
    m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__get_function__SetJoints_Request__values(untyped_member, index));
  const double * value =
    (const double *)(untyped_value);
  *item = *value;
}

bool m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__resize_function__SetJoints_Request__values(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__double__Sequence * member =
    (rosidl_runtime_c__double__Sequence *)(untyped_member);
  rosidl_runtime_c__double__Sequence__fini(member);
  return rosidl_runtime_c__double__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__SetJoints_Request_message_member_array[1] = {
  {
    "values",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(m3pro_teacher_interfaces__srv__SetJoints_Request, values),  // bytes offset in struct
    NULL,  // default value
    m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__size_function__SetJoints_Request__values,  // size() function pointer
    m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__get_const_function__SetJoints_Request__values,  // get_const(index) function pointer
    m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__get_function__SetJoints_Request__values,  // get(index) function pointer
    m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__fetch_function__SetJoints_Request__values,  // fetch(index, &value) function pointer
    m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__assign_function__SetJoints_Request__values,  // assign(index, value) function pointer
    m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__resize_function__SetJoints_Request__values  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__SetJoints_Request_message_members = {
  "m3pro_teacher_interfaces__srv",  // message namespace
  "SetJoints_Request",  // message name
  1,  // number of fields
  sizeof(m3pro_teacher_interfaces__srv__SetJoints_Request),
  m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__SetJoints_Request_message_member_array,  // message members
  m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__SetJoints_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__SetJoints_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__SetJoints_Request_message_type_support_handle = {
  0,
  &m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__SetJoints_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_m3pro_teacher_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, m3pro_teacher_interfaces, srv, SetJoints_Request)() {
  if (!m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__SetJoints_Request_message_type_support_handle.typesupport_identifier) {
    m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__SetJoints_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &m3pro_teacher_interfaces__srv__SetJoints_Request__rosidl_typesupport_introspection_c__SetJoints_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "m3pro_teacher_interfaces/srv/detail/set_joints__rosidl_typesupport_introspection_c.h"
// already included above
// #include "m3pro_teacher_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "m3pro_teacher_interfaces/srv/detail/set_joints__functions.h"
// already included above
// #include "m3pro_teacher_interfaces/srv/detail/set_joints__struct.h"


// Include directives for member types
// Member `message`
#include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void m3pro_teacher_interfaces__srv__SetJoints_Response__rosidl_typesupport_introspection_c__SetJoints_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  m3pro_teacher_interfaces__srv__SetJoints_Response__init(message_memory);
}

void m3pro_teacher_interfaces__srv__SetJoints_Response__rosidl_typesupport_introspection_c__SetJoints_Response_fini_function(void * message_memory)
{
  m3pro_teacher_interfaces__srv__SetJoints_Response__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember m3pro_teacher_interfaces__srv__SetJoints_Response__rosidl_typesupport_introspection_c__SetJoints_Response_message_member_array[2] = {
  {
    "success",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(m3pro_teacher_interfaces__srv__SetJoints_Response, success),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "message",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(m3pro_teacher_interfaces__srv__SetJoints_Response, message),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers m3pro_teacher_interfaces__srv__SetJoints_Response__rosidl_typesupport_introspection_c__SetJoints_Response_message_members = {
  "m3pro_teacher_interfaces__srv",  // message namespace
  "SetJoints_Response",  // message name
  2,  // number of fields
  sizeof(m3pro_teacher_interfaces__srv__SetJoints_Response),
  m3pro_teacher_interfaces__srv__SetJoints_Response__rosidl_typesupport_introspection_c__SetJoints_Response_message_member_array,  // message members
  m3pro_teacher_interfaces__srv__SetJoints_Response__rosidl_typesupport_introspection_c__SetJoints_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  m3pro_teacher_interfaces__srv__SetJoints_Response__rosidl_typesupport_introspection_c__SetJoints_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t m3pro_teacher_interfaces__srv__SetJoints_Response__rosidl_typesupport_introspection_c__SetJoints_Response_message_type_support_handle = {
  0,
  &m3pro_teacher_interfaces__srv__SetJoints_Response__rosidl_typesupport_introspection_c__SetJoints_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_m3pro_teacher_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, m3pro_teacher_interfaces, srv, SetJoints_Response)() {
  if (!m3pro_teacher_interfaces__srv__SetJoints_Response__rosidl_typesupport_introspection_c__SetJoints_Response_message_type_support_handle.typesupport_identifier) {
    m3pro_teacher_interfaces__srv__SetJoints_Response__rosidl_typesupport_introspection_c__SetJoints_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &m3pro_teacher_interfaces__srv__SetJoints_Response__rosidl_typesupport_introspection_c__SetJoints_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "m3pro_teacher_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "m3pro_teacher_interfaces/srv/detail/set_joints__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers m3pro_teacher_interfaces__srv__detail__set_joints__rosidl_typesupport_introspection_c__SetJoints_service_members = {
  "m3pro_teacher_interfaces__srv",  // service namespace
  "SetJoints",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // m3pro_teacher_interfaces__srv__detail__set_joints__rosidl_typesupport_introspection_c__SetJoints_Request_message_type_support_handle,
  NULL  // response message
  // m3pro_teacher_interfaces__srv__detail__set_joints__rosidl_typesupport_introspection_c__SetJoints_Response_message_type_support_handle
};

static rosidl_service_type_support_t m3pro_teacher_interfaces__srv__detail__set_joints__rosidl_typesupport_introspection_c__SetJoints_service_type_support_handle = {
  0,
  &m3pro_teacher_interfaces__srv__detail__set_joints__rosidl_typesupport_introspection_c__SetJoints_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, m3pro_teacher_interfaces, srv, SetJoints_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, m3pro_teacher_interfaces, srv, SetJoints_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_m3pro_teacher_interfaces
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, m3pro_teacher_interfaces, srv, SetJoints)() {
  if (!m3pro_teacher_interfaces__srv__detail__set_joints__rosidl_typesupport_introspection_c__SetJoints_service_type_support_handle.typesupport_identifier) {
    m3pro_teacher_interfaces__srv__detail__set_joints__rosidl_typesupport_introspection_c__SetJoints_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)m3pro_teacher_interfaces__srv__detail__set_joints__rosidl_typesupport_introspection_c__SetJoints_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, m3pro_teacher_interfaces, srv, SetJoints_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, m3pro_teacher_interfaces, srv, SetJoints_Response)()->data;
  }

  return &m3pro_teacher_interfaces__srv__detail__set_joints__rosidl_typesupport_introspection_c__SetJoints_service_type_support_handle;
}
