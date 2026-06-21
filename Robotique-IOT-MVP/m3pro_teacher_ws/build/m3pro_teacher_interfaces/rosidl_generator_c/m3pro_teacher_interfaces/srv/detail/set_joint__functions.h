// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from m3pro_teacher_interfaces:srv/SetJoint.idl
// generated code does not contain a copyright notice

#ifndef M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINT__FUNCTIONS_H_
#define M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINT__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "m3pro_teacher_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "m3pro_teacher_interfaces/srv/detail/set_joint__struct.h"

/// Initialize srv/SetJoint message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * m3pro_teacher_interfaces__srv__SetJoint_Request
 * )) before or use
 * m3pro_teacher_interfaces__srv__SetJoint_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
bool
m3pro_teacher_interfaces__srv__SetJoint_Request__init(m3pro_teacher_interfaces__srv__SetJoint_Request * msg);

/// Finalize srv/SetJoint message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
void
m3pro_teacher_interfaces__srv__SetJoint_Request__fini(m3pro_teacher_interfaces__srv__SetJoint_Request * msg);

/// Create srv/SetJoint message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * m3pro_teacher_interfaces__srv__SetJoint_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
m3pro_teacher_interfaces__srv__SetJoint_Request *
m3pro_teacher_interfaces__srv__SetJoint_Request__create();

/// Destroy srv/SetJoint message.
/**
 * It calls
 * m3pro_teacher_interfaces__srv__SetJoint_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
void
m3pro_teacher_interfaces__srv__SetJoint_Request__destroy(m3pro_teacher_interfaces__srv__SetJoint_Request * msg);

/// Check for srv/SetJoint message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
bool
m3pro_teacher_interfaces__srv__SetJoint_Request__are_equal(const m3pro_teacher_interfaces__srv__SetJoint_Request * lhs, const m3pro_teacher_interfaces__srv__SetJoint_Request * rhs);

/// Copy a srv/SetJoint message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
bool
m3pro_teacher_interfaces__srv__SetJoint_Request__copy(
  const m3pro_teacher_interfaces__srv__SetJoint_Request * input,
  m3pro_teacher_interfaces__srv__SetJoint_Request * output);

/// Initialize array of srv/SetJoint messages.
/**
 * It allocates the memory for the number of elements and calls
 * m3pro_teacher_interfaces__srv__SetJoint_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
bool
m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence__init(m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence * array, size_t size);

/// Finalize array of srv/SetJoint messages.
/**
 * It calls
 * m3pro_teacher_interfaces__srv__SetJoint_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
void
m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence__fini(m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence * array);

/// Create array of srv/SetJoint messages.
/**
 * It allocates the memory for the array and calls
 * m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence *
m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence__create(size_t size);

/// Destroy array of srv/SetJoint messages.
/**
 * It calls
 * m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
void
m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence__destroy(m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence * array);

/// Check for srv/SetJoint message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
bool
m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence__are_equal(const m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence * lhs, const m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence * rhs);

/// Copy an array of srv/SetJoint messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
bool
m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence__copy(
  const m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence * input,
  m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence * output);

/// Initialize srv/SetJoint message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * m3pro_teacher_interfaces__srv__SetJoint_Response
 * )) before or use
 * m3pro_teacher_interfaces__srv__SetJoint_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
bool
m3pro_teacher_interfaces__srv__SetJoint_Response__init(m3pro_teacher_interfaces__srv__SetJoint_Response * msg);

/// Finalize srv/SetJoint message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
void
m3pro_teacher_interfaces__srv__SetJoint_Response__fini(m3pro_teacher_interfaces__srv__SetJoint_Response * msg);

/// Create srv/SetJoint message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * m3pro_teacher_interfaces__srv__SetJoint_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
m3pro_teacher_interfaces__srv__SetJoint_Response *
m3pro_teacher_interfaces__srv__SetJoint_Response__create();

/// Destroy srv/SetJoint message.
/**
 * It calls
 * m3pro_teacher_interfaces__srv__SetJoint_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
void
m3pro_teacher_interfaces__srv__SetJoint_Response__destroy(m3pro_teacher_interfaces__srv__SetJoint_Response * msg);

/// Check for srv/SetJoint message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
bool
m3pro_teacher_interfaces__srv__SetJoint_Response__are_equal(const m3pro_teacher_interfaces__srv__SetJoint_Response * lhs, const m3pro_teacher_interfaces__srv__SetJoint_Response * rhs);

/// Copy a srv/SetJoint message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
bool
m3pro_teacher_interfaces__srv__SetJoint_Response__copy(
  const m3pro_teacher_interfaces__srv__SetJoint_Response * input,
  m3pro_teacher_interfaces__srv__SetJoint_Response * output);

/// Initialize array of srv/SetJoint messages.
/**
 * It allocates the memory for the number of elements and calls
 * m3pro_teacher_interfaces__srv__SetJoint_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
bool
m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence__init(m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence * array, size_t size);

/// Finalize array of srv/SetJoint messages.
/**
 * It calls
 * m3pro_teacher_interfaces__srv__SetJoint_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
void
m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence__fini(m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence * array);

/// Create array of srv/SetJoint messages.
/**
 * It allocates the memory for the array and calls
 * m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence *
m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence__create(size_t size);

/// Destroy array of srv/SetJoint messages.
/**
 * It calls
 * m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
void
m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence__destroy(m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence * array);

/// Check for srv/SetJoint message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
bool
m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence__are_equal(const m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence * lhs, const m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence * rhs);

/// Copy an array of srv/SetJoint messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_m3pro_teacher_interfaces
bool
m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence__copy(
  const m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence * input,
  m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINT__FUNCTIONS_H_
