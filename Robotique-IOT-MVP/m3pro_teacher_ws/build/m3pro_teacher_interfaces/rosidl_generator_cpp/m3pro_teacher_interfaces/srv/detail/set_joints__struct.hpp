// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from m3pro_teacher_interfaces:srv/SetJoints.idl
// generated code does not contain a copyright notice

#ifndef M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINTS__STRUCT_HPP_
#define M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINTS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__m3pro_teacher_interfaces__srv__SetJoints_Request __attribute__((deprecated))
#else
# define DEPRECATED__m3pro_teacher_interfaces__srv__SetJoints_Request __declspec(deprecated)
#endif

namespace m3pro_teacher_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct SetJoints_Request_
{
  using Type = SetJoints_Request_<ContainerAllocator>;

  explicit SetJoints_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
  }

  explicit SetJoints_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
    (void)_alloc;
  }

  // field types and members
  using _values_type =
    std::vector<double, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<double>>;
  _values_type values;

  // setters for named parameter idiom
  Type & set__values(
    const std::vector<double, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<double>> & _arg)
  {
    this->values = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    m3pro_teacher_interfaces::srv::SetJoints_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const m3pro_teacher_interfaces::srv::SetJoints_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<m3pro_teacher_interfaces::srv::SetJoints_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<m3pro_teacher_interfaces::srv::SetJoints_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      m3pro_teacher_interfaces::srv::SetJoints_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<m3pro_teacher_interfaces::srv::SetJoints_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      m3pro_teacher_interfaces::srv::SetJoints_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<m3pro_teacher_interfaces::srv::SetJoints_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<m3pro_teacher_interfaces::srv::SetJoints_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<m3pro_teacher_interfaces::srv::SetJoints_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__m3pro_teacher_interfaces__srv__SetJoints_Request
    std::shared_ptr<m3pro_teacher_interfaces::srv::SetJoints_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__m3pro_teacher_interfaces__srv__SetJoints_Request
    std::shared_ptr<m3pro_teacher_interfaces::srv::SetJoints_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SetJoints_Request_ & other) const
  {
    if (this->values != other.values) {
      return false;
    }
    return true;
  }
  bool operator!=(const SetJoints_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SetJoints_Request_

// alias to use template instance with default allocator
using SetJoints_Request =
  m3pro_teacher_interfaces::srv::SetJoints_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace m3pro_teacher_interfaces


#ifndef _WIN32
# define DEPRECATED__m3pro_teacher_interfaces__srv__SetJoints_Response __attribute__((deprecated))
#else
# define DEPRECATED__m3pro_teacher_interfaces__srv__SetJoints_Response __declspec(deprecated)
#endif

namespace m3pro_teacher_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct SetJoints_Response_
{
  using Type = SetJoints_Response_<ContainerAllocator>;

  explicit SetJoints_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  explicit SetJoints_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _message_type message;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }
  Type & set__message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->message = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    m3pro_teacher_interfaces::srv::SetJoints_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const m3pro_teacher_interfaces::srv::SetJoints_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<m3pro_teacher_interfaces::srv::SetJoints_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<m3pro_teacher_interfaces::srv::SetJoints_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      m3pro_teacher_interfaces::srv::SetJoints_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<m3pro_teacher_interfaces::srv::SetJoints_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      m3pro_teacher_interfaces::srv::SetJoints_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<m3pro_teacher_interfaces::srv::SetJoints_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<m3pro_teacher_interfaces::srv::SetJoints_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<m3pro_teacher_interfaces::srv::SetJoints_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__m3pro_teacher_interfaces__srv__SetJoints_Response
    std::shared_ptr<m3pro_teacher_interfaces::srv::SetJoints_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__m3pro_teacher_interfaces__srv__SetJoints_Response
    std::shared_ptr<m3pro_teacher_interfaces::srv::SetJoints_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SetJoints_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const SetJoints_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SetJoints_Response_

// alias to use template instance with default allocator
using SetJoints_Response =
  m3pro_teacher_interfaces::srv::SetJoints_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace m3pro_teacher_interfaces

namespace m3pro_teacher_interfaces
{

namespace srv
{

struct SetJoints
{
  using Request = m3pro_teacher_interfaces::srv::SetJoints_Request;
  using Response = m3pro_teacher_interfaces::srv::SetJoints_Response;
};

}  // namespace srv

}  // namespace m3pro_teacher_interfaces

#endif  // M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINTS__STRUCT_HPP_
