// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from m3pro_teacher_interfaces:srv/SetJoint.idl
// generated code does not contain a copyright notice

#ifndef M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINT__TRAITS_HPP_
#define M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "m3pro_teacher_interfaces/srv/detail/set_joint__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace m3pro_teacher_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const SetJoint_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: value
  {
    out << "value: ";
    rosidl_generator_traits::value_to_yaml(msg.value, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const SetJoint_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: value
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "value: ";
    rosidl_generator_traits::value_to_yaml(msg.value, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const SetJoint_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace m3pro_teacher_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use m3pro_teacher_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const m3pro_teacher_interfaces::srv::SetJoint_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  m3pro_teacher_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use m3pro_teacher_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const m3pro_teacher_interfaces::srv::SetJoint_Request & msg)
{
  return m3pro_teacher_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<m3pro_teacher_interfaces::srv::SetJoint_Request>()
{
  return "m3pro_teacher_interfaces::srv::SetJoint_Request";
}

template<>
inline const char * name<m3pro_teacher_interfaces::srv::SetJoint_Request>()
{
  return "m3pro_teacher_interfaces/srv/SetJoint_Request";
}

template<>
struct has_fixed_size<m3pro_teacher_interfaces::srv::SetJoint_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<m3pro_teacher_interfaces::srv::SetJoint_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<m3pro_teacher_interfaces::srv::SetJoint_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace m3pro_teacher_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const SetJoint_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << ", ";
  }

  // member: message
  {
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const SetJoint_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << "\n";
  }

  // member: message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const SetJoint_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace m3pro_teacher_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use m3pro_teacher_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const m3pro_teacher_interfaces::srv::SetJoint_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  m3pro_teacher_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use m3pro_teacher_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const m3pro_teacher_interfaces::srv::SetJoint_Response & msg)
{
  return m3pro_teacher_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<m3pro_teacher_interfaces::srv::SetJoint_Response>()
{
  return "m3pro_teacher_interfaces::srv::SetJoint_Response";
}

template<>
inline const char * name<m3pro_teacher_interfaces::srv::SetJoint_Response>()
{
  return "m3pro_teacher_interfaces/srv/SetJoint_Response";
}

template<>
struct has_fixed_size<m3pro_teacher_interfaces::srv::SetJoint_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<m3pro_teacher_interfaces::srv::SetJoint_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<m3pro_teacher_interfaces::srv::SetJoint_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<m3pro_teacher_interfaces::srv::SetJoint>()
{
  return "m3pro_teacher_interfaces::srv::SetJoint";
}

template<>
inline const char * name<m3pro_teacher_interfaces::srv::SetJoint>()
{
  return "m3pro_teacher_interfaces/srv/SetJoint";
}

template<>
struct has_fixed_size<m3pro_teacher_interfaces::srv::SetJoint>
  : std::integral_constant<
    bool,
    has_fixed_size<m3pro_teacher_interfaces::srv::SetJoint_Request>::value &&
    has_fixed_size<m3pro_teacher_interfaces::srv::SetJoint_Response>::value
  >
{
};

template<>
struct has_bounded_size<m3pro_teacher_interfaces::srv::SetJoint>
  : std::integral_constant<
    bool,
    has_bounded_size<m3pro_teacher_interfaces::srv::SetJoint_Request>::value &&
    has_bounded_size<m3pro_teacher_interfaces::srv::SetJoint_Response>::value
  >
{
};

template<>
struct is_service<m3pro_teacher_interfaces::srv::SetJoint>
  : std::true_type
{
};

template<>
struct is_service_request<m3pro_teacher_interfaces::srv::SetJoint_Request>
  : std::true_type
{
};

template<>
struct is_service_response<m3pro_teacher_interfaces::srv::SetJoint_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINT__TRAITS_HPP_
