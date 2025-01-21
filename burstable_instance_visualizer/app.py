import time
import random
import pandas as pd
import streamlit as st


from instance_types import ec2_burstable_instances
from calculate import (
    calculate_earned_credit,
    calculate_max_credit,
    calculate_spent_credit,
)


"""
# Burstable Instance Visualizer.

This is an interactive burstable instance visualizer which simulates how the `accrued_credits`, `earned_credits` and `spent_credits` change with each parameters.

## Parameters
"""


ec2_instance_types = ec2_burstable_instances.keys()

selected_instance_type = st.selectbox("EC2 Instance Type", ec2_instance_types)


baseline = (
    st.number_input(
        "Baseline Usage",
        min_value=0,
        max_value=100,
        value=ec2_burstable_instances[selected_instance_type]["baseline"],
    )
    or 0
)

vcpu_count = (
    st.text_input(
        "vCPU Count",
        value=ec2_burstable_instances[selected_instance_type]["vCPUs"],
    )
    or "0"
)

"""
## Calculated Values
"""

"""
Credits earned continuously by an instance when it is running.



Number of credits earned per second = % baseline utilization * number of vCPUs / 60 minutes
"""

st.text_input(
    "CPU Credits Per Second",
    value=calculate_earned_credit(
        baseline=baseline / 100, vcpu_count=int(vcpu_count), milliseconds=1000
    )
    / 24,
    disabled=True,
)
"""
Number of credits earned per hour = % baseline utilization * number of vCPUs * 60 minutes
"""

st.text_input(
    "CPU Credits Per Hour",
    value=calculate_max_credit(baseline=baseline / 100, vcpu_count=int(vcpu_count))
    / 24,
    disabled=True,
)

"""
Max CPU Credits depends on the instance size but in general is equal to the number of maximum credits earned in 24 hours.
"""

st.text_input(
    "Max CPU Credits",
    value=calculate_max_credit(baseline=baseline / 100, vcpu_count=int(vcpu_count)),
    disabled=True,
)


"""
## Simulation Parameters
Set your maximum and minimum CPU utilization for the simulation.
"""

col1, col2 = st.columns(2)

min_cpu_utilization = col1.number_input(
    "Minimum CPU Utilization",
    min_value=0,
    max_value=100,
    value=0,
)
max_cpu_utilization = col2.number_input(
    "Maximum CPU Utilization",
    min_value=0,
    max_value=100,
    value=100,
)

speed = st.slider("Speed of Simulation", min_value=1, value=1)

if min_cpu_utilization > max_cpu_utilization:
    st.error("Error: Minimum value cannot be greater than maximum value.")

baseline = ec2_burstable_instances[selected_instance_type]["baseline"] / 100
vcpu_count = ec2_burstable_instances[selected_instance_type]["vCPUs"]

cpu_utilization_container = st.empty()

max_credit = calculate_max_credit(baseline=baseline, vcpu_count=vcpu_count)

cpu_utilization_chart_container = st.empty()

overall_change = st.empty()

accrued_credit_chart_container = st.empty()

data = pd.DataFrame(
    {
        "cpu_utilization": [],
        "accrued_credit": [],
        "earned_credit": [],
        "spent_credit": [],
    }
)


accrued_credit = max_credit

while True:
    cpu_utilization = random.randrange(
        min_cpu_utilization,
        max_cpu_utilization + 1,
    )

    cpu_utilization_container.write(f"CPU Utilization: {cpu_utilization}%")

    earned_credit = calculate_earned_credit(
        baseline=baseline,
        vcpu_count=vcpu_count,
        milliseconds=1000,
    )

    spent_credit = calculate_spent_credit(
        baseline=baseline,
        vcpu_count=vcpu_count,
        utilization=cpu_utilization / 100,
        milliseconds=1000,
    )

    accrued_credit = accrued_credit + (earned_credit - spent_credit)
    accrued_credit = min(accrued_credit, max_credit)

    new_df = pd.DataFrame(
        {
            "cpu_utilization": [cpu_utilization],
            "accrued_credit": [accrued_credit],
            "spent_credit": [spent_credit],
            "earned_credit": [earned_credit],
        }
    )

    data = pd.concat([data, new_df], ignore_index=True)

    cpu_utilization_chart_container.line_chart(
        data[["cpu_utilization"]],
        x_label="Time",
        y_label="CPU Utilization",
    )

    if earned_credit >= spent_credit:
        overall_change.write(f"""
        **Last Change**: +{earned_credit-spent_credit:.5f} (Earned)

        **Accrued Credit**: {accrued_credit:.5f}
        """)
    else:
        overall_change.write(f"""
        **Last Change**: -{spent_credit-earned_credit:.5f} (Spent)

        **Accrued Credit**: {accrued_credit:.5f}
        """)

    accrued_credit_chart_container.line_chart(
        data[["accrued_credit"]],
        x_label="Time",
        y_label="Accrued Credits",
    )

    time.sleep(1 / speed)
