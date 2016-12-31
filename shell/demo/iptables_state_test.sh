#!/bin/bash
#测试iptables状态
physical_interface=eth0

#physical_interface
iptables -t filter -A INPUT -i ${physical_interface} -m state --state NEW -j LOG --log-prefix "${physical_interface}_INPUT_NEW "
iptables -t filter -A INPUT -i ${physical_interface} -m state --state ESTABLISHED -j LOG --log-prefix "${physical_interface}_INPUT_ESTAB "
iptables -t filter -A INPUT -i ${physical_interface} -m state --state RELATED -j LOG --log-prefix "${physical_interface}_INPUT_RELATED "
iptables -t filter -A INPUT -i ${physical_interface} -m state --state INVALID -j LOG --log-prefix "${physical_interface}_INPUT_INVALIED "

iptables -t filter -A OUTPUT -o ${physical_interface} -m state --state NEW -j LOG --log-prefix "${physical_interface}_OUTPUT_NEW "
iptables -t filter -A OUTPUT -o ${physical_interface} -m state --state ESTABLISHED -j LOG --log-prefix "${physical_interface}_OUTPUT_ESTAB "
iptables -t filter -A OUTPUT -o ${physical_interface} -m state --state RELATED -j LOG --log-prefix "${physical_interface}_OUTPUT_RELATED "
iptables -t filter -A OUTPUT -o ${physical_interface} -m state --state INVALID -j LOG --log-prefix "${physical_interface}_OUTPUT_INVALIED "

#lo
iptables -t filter -A INPUT -i lo -m state --state NEW -j LOG --log-prefix "lo_INPUT_NEW "
iptables -t filter -A INPUT -i lo -m state --state ESTABLISHED -j LOG --log-prefix "lo_INPUT_ESTAB "
iptables -t filter -A INPUT -i lo -m state --state RELATED -j LOG --log-prefix "lo_INPUT_RELATED "
iptables -t filter -A INPUT -i lo -m state --state INVALID -j LOG --log-prefix "lo_INPUT_INVALIED "

iptables -t filter -A OUTPUT -o lo -m state --state NEW -j LOG --log-prefix "lo_OUTPUT_NEW "
iptables -t filter -A OUTPUT -o lo -m state --state ESTABLISHED -j LOG --log-prefix "lo_OUTPUT_ESTAB "
iptables -t filter -A OUTPUT -o lo -m state --state RELATED -j LOG --log-prefix "lo_OUTPUT_RELATED "
iptables -t filter -A OUTPUT -o lo -m state --state INVALID -j LOG --log-prefix "lo_OUTPUT_INVALIED "

#physical_interface
iptables -t filter -A POSTROUTING -i ${physical_interface} -m state --state NEW -j LOG --log-prefix "${physical_interface}_POSTROUTING_NEW "
iptables -t filter -A POSTROUTING -i ${physical_interface} -m state --state ESTABLISHED -j LOG --log-prefix "${physical_interface}_POSTROUTING_ESTAB "
iptables -t filter -A POSTROUTING -i ${physical_interface} -m state --state RELATED -j LOG --log-prefix "${physical_interface}_POSTROUTING_RELATED "
iptables -t filter -A POSTROUTING -i ${physical_interface} -m state --state INVALID -j LOG --log-prefix "${physical_interface}_POSTROUTING_INVALIED "

iptables -t filter -A POSTROUTING -o ${physical_interface} -m state --state NEW -j LOG --log-prefix "${physical_interface}_POSTROUTING_NEW "
iptables -t filter -A POSTROUTING -o ${physical_interface} -m state --state ESTABLISHED -j LOG --log-prefix "${physical_interface}_POSTROUTING_ESTAB "
iptables -t filter -A POSTROUTING -o ${physical_interface} -m state --state RELATED -j LOG --log-prefix "${physical_interface}_POSTROUTING_RELATED "
iptables -t filter -A POSTROUTING -o ${physical_interface} -m state --state INVALID -j LOG --log-prefix "${physical_interface}_POSTROUTING_INVALIED "

#lo
iptables -t filter -A POSTROUTING -i lo -m state --state NEW -j LOG --log-prefix "lo_POSTROUTING_NEW "
iptables -t filter -A POSTROUTING -i lo -m state --state ESTABLISHED -j LOG --log-prefix "lo_POSTROUTING_ESTAB "
iptables -t filter -A POSTROUTING -i lo -m state --state RELATED -j LOG --log-prefix "lo_POSTROUTING_RELATED "
iptables -t filter -A POSTROUTING -i lo -m state --state INVALID -j LOG --log-prefix "lo_POSTROUTING_INVALIED "

iptables -t filter -A POSTROUTING -o lo -m state --state NEW -j LOG --log-prefix "lo_POSTROUTING_NEW "
iptables -t filter -A POSTROUTING -o lo -m state --state ESTABLISHED -j LOG --log-prefix "lo_POSTROUTING_ESTAB "
iptables -t filter -A POSTROUTING -o lo -m state --state RELATED -j LOG --log-prefix "lo_POSTROUTING_RELATED "
iptables -t filter -A POSTROUTING -o lo -m state --state INVALID -j LOG --log-prefix "lo_POSTROUTING_INVALIED "

