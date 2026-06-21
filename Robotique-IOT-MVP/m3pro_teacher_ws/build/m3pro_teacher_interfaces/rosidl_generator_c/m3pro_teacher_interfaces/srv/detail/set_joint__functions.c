// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from m3pro_teacher_interfaces:srv/SetJoint.idl
// generated code does not contain a copyright notice
#include "m3pro_teacher_interfaces/srv/detail/set_joint__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

bool
m3pro_teacher_interfaces__srv__SetJoint_Request__init(m3pro_teacher_interfaces__srv__SetJoint_Request * msg)
{
  if (!msg) {
    return false;
  }
  // value
  return true;
}

void
m3pro_teacher_interfaces__srv__SetJoint_Request__fini(m3pro_teacher_interfaces__srv__SetJoint_Request * msg)
{
  if (!msg) {
    return;
  }
  // value
}

bool
m3pro_teacher_interfaces__srv__SetJoint_Request__are_equal(const m3pro_teacher_interfaces__srv__SetJoint_Request * lhs, const m3pro_teacher_interfaces__srv__SetJoint_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // value
  if (lhs->value != rhs->value) {
    return false;
  }
  return true;
}

bool
m3pro_teacher_interfaces__srv__SetJoint_Request__copy(
  const m3pro_teacher_interfaces__srv__SetJoint_Request * input,
  m3pro_teacher_interfaces__srv__SetJoint_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // value
  output->value = input->value;
  return true;
}

m3pro_teacher_interfaces__srv__SetJoint_Request *
m3pro_teacher_interfaces__srv__SetJoint_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  m3pro_teacher_interfaces__srv__SetJoint_Request * msg = (m3pro_teacher_interfaces__srv__SetJoint_Request *)allocator.allocate(sizeof(m3pro_teacher_interfaces__srv__SetJoint_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(m3pro_teacher_interfaces__srv__SetJoint_Request));
  bool success = m3pro_teacher_interfaces__srv__SetJoint_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
m3pro_teacher_interfaces__srv__SetJoint_Request__destroy(m3pro_teacher_interfaces__srv__SetJoint_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    m3pro_teacher_interfaces__srv__SetJoint_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence__init(m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  m3pro_teacher_interfaces__srv__SetJoint_Request * data = NULL;

  if (size) {
    data = (m3pro_teacher_interfaces__srv__SetJoint_Request *)allocator.zero_allocate(size, sizeof(m3pro_teacher_interfaces__srv__SetJoint_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = m3pro_teacher_interfaces__srv__SetJoint_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        m3pro_teacher_interfaces__srv__SetJoint_Request__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence__fini(m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      m3pro_teacher_interfaces__srv__SetJoint_Request__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence *
m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence * array = (m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence *)allocator.allocate(sizeof(m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence__destroy(m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence__are_equal(const m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence * lhs, const m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!m3pro_teacher_interfaces__srv__SetJoint_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence__copy(
  const m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence * input,
  m3pro_teacher_interfaces__srv__SetJoint_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(m3pro_teacher_interfaces__srv__SetJoint_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    m3pro_teacher_interfaces__srv__SetJoint_Request * data =
      (m3pro_teacher_interfaces__srv__SetJoint_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!m3pro_teacher_interfaces__srv__SetJoint_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          m3pro_teacher_interfaces__srv__SetJoint_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!m3pro_teacher_interfaces__srv__SetJoint_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `message`
#include "rosidl_runtime_c/string_functions.h"

bool
m3pro_teacher_interfaces__srv__SetJoint_Response__init(m3pro_teacher_interfaces__srv__SetJoint_Response * msg)
{
  if (!msg) {
    return false;
  }
  // success
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    m3pro_teacher_interfaces__srv__SetJoint_Response__fini(msg);
    return false;
  }
  return true;
}

void
m3pro_teacher_interfaces__srv__SetJoint_Response__fini(m3pro_teacher_interfaces__srv__SetJoint_Response * msg)
{
  if (!msg) {
    return;
  }
  // success
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
m3pro_teacher_interfaces__srv__SetJoint_Response__are_equal(const m3pro_teacher_interfaces__srv__SetJoint_Response * lhs, const m3pro_teacher_interfaces__srv__SetJoint_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->message), &(rhs->message)))
  {
    return false;
  }
  return true;
}

bool
m3pro_teacher_interfaces__srv__SetJoint_Response__copy(
  const m3pro_teacher_interfaces__srv__SetJoint_Response * input,
  m3pro_teacher_interfaces__srv__SetJoint_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // success
  output->success = input->success;
  // message
  if (!rosidl_runtime_c__String__copy(
      &(input->message), &(output->message)))
  {
    return false;
  }
  return true;
}

m3pro_teacher_interfaces__srv__SetJoint_Response *
m3pro_teacher_interfaces__srv__SetJoint_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  m3pro_teacher_interfaces__srv__SetJoint_Response * msg = (m3pro_teacher_interfaces__srv__SetJoint_Response *)allocator.allocate(sizeof(m3pro_teacher_interfaces__srv__SetJoint_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(m3pro_teacher_interfaces__srv__SetJoint_Response));
  bool success = m3pro_teacher_interfaces__srv__SetJoint_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
m3pro_teacher_interfaces__srv__SetJoint_Response__destroy(m3pro_teacher_interfaces__srv__SetJoint_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    m3pro_teacher_interfaces__srv__SetJoint_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence__init(m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  m3pro_teacher_interfaces__srv__SetJoint_Response * data = NULL;

  if (size) {
    data = (m3pro_teacher_interfaces__srv__SetJoint_Response *)allocator.zero_allocate(size, sizeof(m3pro_teacher_interfaces__srv__SetJoint_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = m3pro_teacher_interfaces__srv__SetJoint_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        m3pro_teacher_interfaces__srv__SetJoint_Response__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence__fini(m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      m3pro_teacher_interfaces__srv__SetJoint_Response__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence *
m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence * array = (m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence *)allocator.allocate(sizeof(m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence__destroy(m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence__are_equal(const m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence * lhs, const m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!m3pro_teacher_interfaces__srv__SetJoint_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence__copy(
  const m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence * input,
  m3pro_teacher_interfaces__srv__SetJoint_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(m3pro_teacher_interfaces__srv__SetJoint_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    m3pro_teacher_interfaces__srv__SetJoint_Response * data =
      (m3pro_teacher_interfaces__srv__SetJoint_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!m3pro_teacher_interfaces__srv__SetJoint_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          m3pro_teacher_interfaces__srv__SetJoint_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!m3pro_teacher_interfaces__srv__SetJoint_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
