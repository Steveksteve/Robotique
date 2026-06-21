// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from m3pro_teacher_interfaces:srv/SetJoints.idl
// generated code does not contain a copyright notice

#ifndef M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINTS__TRAITS_HPP_
#define M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINTS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "m3pro_teacher_interfaces/srv/detail/set_joints__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace m3pro_teacher_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const SetJoints_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: values
  {
    if (msg.values.size() == 0) {
      out << "values: []";
    } else {
      out << "values: [";
      size_t pending_items = msg.values.size();
      for (auto item : msg.values) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const SetJoints_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: values
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.values.size() == 0) {
      out << "values: []\n";
    } else {
      out << "values:\n";
      for (auto item : msg.values) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const SetJoints_Request & msg, bool use_flow_style = false)
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
  const m3pro_teacher_interfaces::srv::SetJoints_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  m3pro_teacher_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use m3pro_teacher_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const m3pro_teacher_interfaces::srv::SetJoints_Request & msg)
{
  return m3pro_teacher_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<m3pro_teacher_interfaces::srv::SetJoints_Request>()
{
  return "m3pro_teacher_interfaces::srv::SetJoints_Request";
}

template<>
inline const char * name<m3pro_teacher_interfaces::srv::SetJoints_Request>()
{
  return "m3pro_teacher_interfaces/srv/SetJoints_Request";
}

template<>
struct has_fixed_size<m3pro_teacher_interfaces::srv::SetJoints_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<m3pro_teacher_interfaces::srv::SetJoints_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<m3pro_teacher_interfaces::srv::SetJoints_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace m3pro_teacher_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const SetJoints_Response & msg,
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
  const SetJoints_Response & msg,
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

inline std::string to_yaml(const SetJoints_Response & msg, bool use_flow_style = false)
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
  const m3pro_teacher_interfaces::srv::SetJoints_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  m3pro_teacher_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use m3pro_teacher_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const m3pro_teacher_interfaces::srv::SetJoints_Response & msg)
{
  return m3pro_teacher_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<m3pro_teacher_interfaces::srv::SetJoints_Response>()
{
  return "m3pro_teacher_interfaces::srv::SetJoints_Response";
}

template<>
inline const char * name<m3pro_teacher_interfaces::srv::SetJoints_Response>()
{
  return "m3pro_teacher_interfaces/srv/SetJoints_Response";
}

template<>
struct has_fixed_size<m3pro_teacher_interfaces::srv::SetJoints_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<m3pro_teacher_interfaces::srv::SetJoints_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<m3pro_teacher_interfaces::srv::SetJoints_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<m3pro_teacher_interfaces::srv::SetJoints>()
{
  return "m3pro_teacher_interfaces::srv::SetJoints";
}

template<>
inline const char * name<m3pro_teacher_interfaces::srv::SetJoints>()
{
  return "m3pro_teacher_interfaces/srv/SetJoints";
}

template<>
struct has_fixed_size<m3pro_teacher_interfaces::srv::SetJoints>
  : std::integral_constant<
    bool,
    has_fixed_size<m3pro_teacher_interfaces::srv::SetJoints_Request>::value &&
    has_fixed_size<m3pro_teacher_interfaces::srv::SetJoints_Response>::value
  >
{
};

template<>
struct has_bounded_size<m3pro_teacher_interfaces::srv::SetJoints>
  : std::integral_constant<
    bool,
    has_bounded_size<m3pro_teacher_interfaces::srv::SetJoints_Request>::value &&
    has_bounded_size<m3pro_teacher_interfaces::srv::SetJoints_Response>::value
  >
{
};

template<>
struct is_service<m3pro_teacher_interfaces::srv::SetJoints>
  : std::true_type
{
};

template<>
struct is_service_request<m3pro_teacher_interfaces::srv::SetJoints_Request>
  : std::true_type
{
};

template<>
struct is_service_response<m3pro_teacher_interfaces::srv::SetJoints_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // M3PRO_TEACHER_INTERFACES__SRV__DETAIL__SET_JOINTS__TRAITS_HPP_
