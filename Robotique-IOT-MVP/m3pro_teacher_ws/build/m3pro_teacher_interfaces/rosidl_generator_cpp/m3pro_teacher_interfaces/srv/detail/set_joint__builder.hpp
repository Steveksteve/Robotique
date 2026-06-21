// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from m3pro_teacher_interfaces:srv/SetJoint.idl
// generated code does not contain a copyright notice

#ifndef M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINT__BUILDER_HPP_
#define M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "m3pro_teacher_interfaces/srv/detail/set_joint__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace m3pro_teacher_interfaces
{

namespace srv
{

namespace builder
{

class Init_SetJoint_Request_value
{
public:
  Init_SetJoint_Request_value()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::m3pro_teacher_interfaces::srv::SetJoint_Request value(::m3pro_teacher_interfaces::srv::SetJoint_Request::_value_type arg)
  {
    msg_.value = std::move(arg);
    return std::move(msg_);
  }

private:
  ::m3pro_teacher_interfaces::srv::SetJoint_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::m3pro_teacher_interfaces::srv::SetJoint_Request>()
{
  return m3pro_teacher_interfaces::srv::builder::Init_SetJoint_Request_value();
}

}  // namespace m3pro_teacher_interfaces


namespace m3pro_teacher_interfaces
{

namespace srv
{

namespace builder
{

class Init_SetJoint_Response_message
{
public:
  explicit Init_SetJoint_Response_message(::m3pro_teacher_interfaces::srv::SetJoint_Response & msg)
  : msg_(msg)
  {}
  ::m3pro_teacher_interfaces::srv::SetJoint_Response message(::m3pro_teacher_interfaces::srv::SetJoint_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::m3pro_teacher_interfaces::srv::SetJoint_Response msg_;
};

class Init_SetJoint_Response_success
{
public:
  Init_SetJoint_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SetJoint_Response_message success(::m3pro_teacher_interfaces::srv::SetJoint_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_SetJoint_Response_message(msg_);
  }

private:
  ::m3pro_teacher_interfaces::srv::SetJoint_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::m3pro_teacher_interfaces::srv::SetJoint_Response>()
{
  return m3pro_teacher_interfaces::srv::builder::Init_SetJoint_Response_success();
}

}  // namespace m3pro_teacher_interfaces

#endif  // M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINT__BUILDER_HPP_
