#include <chrono>
#include <memory>
#include <string>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "std_msgs/msg/int32.hpp"
#include "my_package/math_helper.hpp"

using namespace std::chrono_literals;


/*lets make a node that subscribes to a topic, takes in a number, squares it, and publishes to another node*/
class SquareNode : public rclcpp::Node
{
  public:
    SquareNode(): Node("square_node")
    {
      // the 10 refers to the message queue. the subscription/publisher only holds the 10 most recent nodes
      publisher = this->create_publisher<std_msgs::msg::String>("output", 10);

      auto square_callback = [this](std_msgs::msg::Int32::ConstSharedPtr msg) {
        int num = msg->data;
        std_msgs::msg::String output;
        output.data = "The output is " + std::to_string(square(num));
        this->publisher->publish(output);
      };

      subscription = this->create_subscription<std_msgs::msg::Int32>("input", 10, square_callback);
    }
  private:
    rclcpp::Subscription<std_msgs::msg::Int32>::SharedPtr subscription;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SquareNode>());
  rclcpp::shutdown();
  return 0;
}
