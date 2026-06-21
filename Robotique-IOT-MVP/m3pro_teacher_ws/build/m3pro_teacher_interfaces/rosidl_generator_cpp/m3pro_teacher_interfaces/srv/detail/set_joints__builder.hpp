// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from m3pro_teacher_interfaces:srv/SetJoints.idl
// generated code does not contain a copyright notice

#ifndef M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINTS__BUILDER_HPP_
#define M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINTS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "m3pro_teacher_interfaces/srv/detail/set_joints__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace m3pro_teacher_interfaces
{

namespace srv
{

namespace builder
{

class Init_SetJoints_Request_values
{
public:
  Init_SetJoints_Request_values()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::m3pro_teacher_interfaces::srv::SetJoints_Request values(::m3pro_teacher_interfaces::srv::SetJoints_Request::_values_type arg)
  {
    msg_.values = std::move(arg);
    return std::move(msg_);
  }

private:
  ::m3pro_teacher_interfaces::srv::SetJoints_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::m3pro_teacher_interfaces::srv::SetJoints_Request>()
{
  return m3pro_teacher_interfaces::srv::builder::Init_SetJoints_Request_values();
}

}  // namespace m3pro_teacher_interfaces


namespace m3pro_teacher_interfaces
{

namespace srv
{

namespace builder
{

class Init_SetJoints_Response_message
{
public:
  explicit Init_SetJoints_Response_message(::m3pro_teacher_interfaces::srv::SetJoints_Response & msg)
  : msg_(msg)
  {}
  ::m3pro_teacher_interfaces::srv::SetJoints_Response message(::m3pro_teacher_interfaces::srv::SetJoints_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::m3pro_teacher_interfaces::srv::SetJoints_Response msg_;
};

class Init_SetJoints_Response_success
{
public:
  Init_SetJoints_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SetJoints_Response_message success(::m3pro_teacher_interfaces::srv::SetJoints_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_SetJoints_Response_message(msg_);
  }

private:
  ::m3pro_teacher_interfaces::srv::SetJoints_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::m3pro_teacher_interfaces::srv::SetJoints_Response>()
{
  return m3pro_teacher_interfaces::srv::builder::Init_SetJoints_Response_success();
}

}  // namespace m3pro_teacher_interfaces

#endif  // M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINTS__BUILDER_HPP_
