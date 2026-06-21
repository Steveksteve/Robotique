// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from m3pro_teacher_interfaces:srv/SetJoint.idl
// generated code does not contain a copyright notice

#ifndef M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINT__STRUCT_H_
#define M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINT__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in srv/SetJoint in the package m3pro_teacher_interfaces.
typedef struct m3pro_teacher_interfaces__srv__SetJoint_Request
{
  double value;
} m3pro_teacher_interfaces__srv__SetJoint_Request;

// Struct for a sequence of m3pro_teacher_interfaces__srv__SetJoint_Request.
typedef struct m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence
{
  m3pro_teacher_interfaces__srv__SetJoint_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/SetJoint in the package m3pro_teacher_interfaces.
typedef struct m3pro_teacher_interfaces__srv__SetJoint_Response
{
  bool success;
  rosidl_runtime_c__String message;
} m3pro_teacher_interfaces__srv__SetJoint_Response;

// Struct for a sequence of m3pro_teacher_interfaces__srv__SetJoint_Response.
typedef struct m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence
{
  m3pro_teacher_interfaces__srv__SetJoint_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINT__STRUCT_H_
