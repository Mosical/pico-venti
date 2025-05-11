// i2c config
document.getElementById("i2c").onchange = function() {
    document.querySelector("#i2c_entries").innerHTML = '';
    for(var i = 0; i < document.getElementById("i2c").value; i++) {
        var label_sda = document.createElement("label");
        label_sda.setAttribute("for", `i2c_sda_${i}`);
        label_sda.innerHTML = `sda_${i}: `;
        var input_sda = document.createElement("input");
        input_sda.name = `i2c_sda_${i}`;
        input_sda.id = `i2c_sda_${i}`;
        input_sda.type = 'text';
        var label_scl = document.createElement("label");
        label_scl.setAttribute("for", `i2c_scl_${i}`);
        label_scl.innerHTML = `scl_${i}: `;
        var input_scl = document.createElement("input");
        input_scl.name = `i2c_scl_${i}`;
        input_scl.id = `i2c_scl_${i}`;
        input_scl.type = 'text';
        document.getElementById("i2c_entries").append(label_sda);
        document.getElementById("i2c_entries").append(input_sda);
        document.getElementById("i2c_entries").append(document.createElement("br"));
        document.getElementById("i2c_entries").append(label_scl);
        document.getElementById("i2c_entries").append(input_scl);
        document.getElementById("i2c_entries").append(document.createElement("br"));
    }
}
// sht4x config
document.getElementById("sht4x").onchange = function() {
    document.querySelector("#sht4x_entries").innerHTML = '';
    for(var i = 0; i < document.getElementById("sht4x").value; i++) {
        var label_mode = document.createElement("label");
        label_mode.setAttribute("for", `sht4x_mode_${i}`);
        label_mode.innerHTML = `mode_${i}: `;
        var input_mode = document.createElement("input");
        input_mode.name = `sht4x_mode_${i}`;
        input_mode.id = `sht4x_mode_${i}`;
        input_mode.type = 'text';
        var label_channel = document.createElement("label");
        label_channel.setAttribute("for", `sht4x_i2c_channel_${i}`);
        label_channel.innerHTML = `i2c_channel_${i}: `;
        var input_channel = document.createElement("input");
        input_channel.name = `sht4x_i2c_channel_${i}`;
        input_channel.id = `sht4x_i2c_channel_${i}`;
        input_channel.type = 'text';
        var label_address = document.createElement("label");
        label_address.setAttribute("for", `sht4x_i2c_address_${i}`);
        label_address.innerHTML = `i2c_address_${i}: `;
        var input_address = document.createElement("input");
        input_address.name = `sht4x_i2c_address_${i}`;
        input_address.id = `sht4x_i2c_address_${i}`;
        input_address.type = 'text';
        document.getElementById("sht4x_entries").append(label_mode);
        document.getElementById("sht4x_entries").append(input_mode);
        document.getElementById("sht4x_entries").append(document.createElement("br"));
        document.getElementById("sht4x_entries").append(label_channel);
        document.getElementById("sht4x_entries").append(input_channel);
        document.getElementById("sht4x_entries").append(document.createElement("br"));
        document.getElementById("sht4x_entries").append(label_address);
        document.getElementById("sht4x_entries").append(input_address);
        document.getElementById("sht4x_entries").append(document.createElement("br"));
    }
}
// thermistor config
document.getElementById("thermistor").onchange = function() {
    document.querySelector("#thermistor_entries").innerHTML = '';
    for(var i = 0; i < document.getElementById("thermistor").value; i++) {
        var label_pin = document.createElement("label");
        label_pin.setAttribute("for", `thermistor_pin_${i}`);
        label_pin.innerHTML = `pin_${i}: `;
        var input_pin = document.createElement("input");
        input_pin.name = `thermistor_pin_${i}`;
        input_pin.id = `thermistor_pin_${i}`;
        input_pin.type = 'text';
        var label_adc = document.createElement("label");
        label_adc.setAttribute("for", `thermistor_adc_${i}`);
        label_adc.innerHTML = `adc_${i}: `;
        var input_adc = document.createElement("input");
        input_adc.name = `thermistor_adc_${i}`;
        input_adc.id = `thermistor_adc_${i}`;
        input_adc.type = 'text';
        var label_temp = document.createElement("label");
        label_temp.setAttribute("for", `thermistor_temp_${i}`);
        label_temp.innerHTML = `temp_${i}: `;
        var input_temp = document.createElement("input");
        input_temp.name = `thermistor_temp_${i}`;
        input_temp.id = `thermistor_temp_${i}`;
        input_temp.type = 'text';
        var label_beta = document.createElement("label");
        label_beta.setAttribute("for", `thermistor_beta_${i}`);
        label_beta.innerHTML = `beta_${i}: `;
        var input_beta = document.createElement("input");
        input_beta.name = `thermistor_beta_${i}`;
        input_beta.id = `thermistor_beta_${i}`;
        input_beta.type = 'text';
        var label_nominal_resistor = document.createElement("label");
        label_nominal_resistor.setAttribute("for", `thermistor_nominal_resistor_${i}`);
        label_nominal_resistor.innerHTML = `nominal_resistor_${i}: `;
        var input_nominal_resistor = document.createElement("input");
        input_nominal_resistor.name = `thermistor_nominal_resistor_${i}`;
        input_nominal_resistor.id = `thermistor_nominal_resistor_${i}`;
        input_nominal_resistor.type = 'text';
        var label_external_resistor = document.createElement("label");
        label_external_resistor.setAttribute("for", `thermistor_external_resistor_${i}`);
        label_external_resistor.innerHTML = `external_resistor_${i}: `;
        var input_external_resistor = document.createElement("input");
        input_external_resistor.name = `thermistor_external_resistor_${i}`;
        input_external_resistor.id = `thermistor_external_resistor_${i}`;
        input_external_resistor.type = 'text';
        document.getElementById("thermistor_entries").append(label_pin);
        document.getElementById("thermistor_entries").append(input_pin);
        document.getElementById("thermistor_entries").append(document.createElement("br"));
        document.getElementById("thermistor_entries").append(label_adc);
        document.getElementById("thermistor_entries").append(input_adc);
        document.getElementById("thermistor_entries").append(document.createElement("br"));
        document.getElementById("thermistor_entries").append(label_temp);
        document.getElementById("thermistor_entries").append(input_temp);
        document.getElementById("thermistor_entries").append(document.createElement("br"));
        document.getElementById("thermistor_entries").append(label_beta);
        document.getElementById("thermistor_entries").append(input_beta);
        document.getElementById("thermistor_entries").append(document.createElement("br"));
        document.getElementById("thermistor_entries").append(label_nominal_resistor);
        document.getElementById("thermistor_entries").append(input_nominal_resistor);
        document.getElementById("thermistor_entries").append(document.createElement("br"));
        document.getElementById("thermistor_entries").append(label_external_resistor);
        document.getElementById("thermistor_entries").append(input_external_resistor);
        document.getElementById("thermistor_entries").append(document.createElement("br"));
    }
}
// fan config
document.getElementById("fan").onchange = function() {
    document.querySelector("#fan_entries").innerHTML = '';
    for(var i = 0; i < document.getElementById("fan").value; i++) {
        var label_pin = document.createElement("label");
        label_pin.setAttribute("for", `fan_pin_fan_${i}`);
        label_pin.innerHTML = `pin_fan_${i}: `;
        var input_pin = document.createElement("input");
        input_pin.name = `fan_pin_fan_${i}`;
        input_pin.id = `fan_pin_fan_${i}`;
        input_pin.type = 'text';
        var label_temp_type = document.createElement("label");
        label_temp_type.setAttribute("for", `fan_temp_type_${i}`);
        label_temp_type.innerHTML = `temp_type_${i}: `;
        var input_temp_type = document.createElement("input");
        input_temp_type.name = `fan_temp_type_${i}`;
        input_temp_type.id = `fan_temp_type_${i}`;
        input_temp_type.type = 'text';
        var label_temp_instance = document.createElement("label");
        label_temp_instance.setAttribute("for", `fan_temp_instance_${i}`);
        label_temp_instance.innerHTML = `temp_instance_${i}: `;
        var input_temp_instance = document.createElement("input");
        input_temp_instance.name = `fan_temp_instance_${i}`;
        input_temp_instance.id = `fan_temp_instance_${i}`;
        input_temp_instance.type = 'text';
        var label_zero_rpm = document.createElement("label");
        label_zero_rpm.setAttribute("for", `fan_zero_rpm_${i}`);
        label_zero_rpm.innerHTML = `zero_rpm_${i}: `;
        var input_zero_rpm = document.createElement("select");
        input_zero_rpm.name = `fan_zero_rpm_${i}`;
        input_zero_rpm.id = `fan_zero_rpm_${i}`;
        var select_zero_rpm_false = document.createElement("option");
        select_zero_rpm_false.value = false
        select_zero_rpm_false.text = false
        input_zero_rpm.appendChild(select_zero_rpm_false)
        var select_zero_rpm_true = document.createElement("option");
        select_zero_rpm_true.value = true
        select_zero_rpm_true.text = true
        input_zero_rpm.appendChild(select_zero_rpm_true)
        var label_min_temp = document.createElement("label");
        label_min_temp.setAttribute("for", `fan_min_temp_${i}`);
        label_min_temp.innerHTML = `min_temp_${i}: `;
        var input_min_temp = document.createElement("input");
        input_min_temp.name = `fan_min_temp_${i}`;
        input_min_temp.id = `fan_min_temp_${i}`;
        input_min_temp.type = 'text';
        var label_max_temp = document.createElement("label");
        label_max_temp.setAttribute("for", `fan_max_temp_${i}`);
        label_max_temp.innerHTML = `max_temp_${i}: `;
        var input_max_temp = document.createElement("input");
        input_max_temp.name = `fan_max_temp_${i}`;
        input_max_temp.id = `fan_max_temp_${i}`;
        input_max_temp.type = 'text';
        var label_fan_curve = document.createElement("label");
        label_fan_curve.setAttribute("for", `fan_fan_curve_${i}`);
        label_fan_curve.innerHTML = `fan_curve_${i}: `;
        var input_fan_curve = document.createElement("input");
        input_fan_curve.name = `fan_fan_curve_${i}`;
        input_fan_curve.id = `fan_fan_curve_${i}`;
        input_fan_curve.type = 'text';
        document.getElementById("fan_entries").append(label_pin);
        document.getElementById("fan_entries").append(input_pin);
        document.getElementById("fan_entries").append(document.createElement("br"));
        document.getElementById("fan_entries").append(label_temp_type);
        document.getElementById("fan_entries").append(input_temp_type);
        document.getElementById("fan_entries").append(document.createElement("br"));
        document.getElementById("fan_entries").append(label_temp_instance);
        document.getElementById("fan_entries").append(input_temp_instance);
        document.getElementById("fan_entries").append(document.createElement("br"));
        document.getElementById("fan_entries").append(label_zero_rpm);
        document.getElementById("fan_entries").append(input_zero_rpm);
        document.getElementById("fan_entries").append(document.createElement("br"));
        document.getElementById("fan_entries").append(label_min_temp);
        document.getElementById("fan_entries").append(input_min_temp);
        document.getElementById("fan_entries").append(document.createElement("br"));
        document.getElementById("fan_entries").append(label_max_temp);
        document.getElementById("fan_entries").append(input_max_temp);
        document.getElementById("fan_entries").append(document.createElement("br"));
        document.getElementById("fan_entries").append(label_fan_curve);
        document.getElementById("fan_entries").append(input_fan_curve);
        document.getElementById("fan_entries").append(document.createElement("br"));
    }
}