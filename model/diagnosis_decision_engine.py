# # -----------------------------------------
# # Diagnosis + Decision Engine (CSV-Optimized)
# # -----------------------------------------

# class DiagnosisDecisionEngine:

#     def __init__(self):
#         # Thresholds tuned for your CSV (0–1 normalized metrics)
#         self.cpu_high = 0.75
#         self.delay_high = 0.65
#         self.link_util_high = 0.80
#         self.flow_table_high = 0.85
#         self.switch_port_util_high = 0.85
#         self.packet_loss_th = 0.08  # slightly higher because CSV packet_loss is small

#     # =========================================================
#     # 1. DIAGNOSIS ENGINE
#     # =========================================================
#     def diagnose(self, m):

#         cpu = m.get("cpu", 0)
#         delay = m.get("delay", 0)
#         pkt_in = m.get("pkt_in", 0)
#         pkt_out = m.get("pkt_out", 0)
#         flow_table = m.get("flow_table", 0)
#         link_util = m.get("link_util", 0)
#         packet_loss = m.get("packet_loss", 0)
#         switch_util = m.get("switch_util", 0)

#         switch_disconnect = m.get("switch_disconnect", False)
#         controller_heartbeat = m.get("controller_heartbeat", True)
#         rest_api_fail = m.get("rest_api_fail", False)

#         lstm_flag = m.get("lstm_anomaly", False)
#         if_flag = m.get("if_anomaly", False)

#         # ------------------------------
#         # CONTROLLER HEALTH RULES
#         # ------------------------------
#         if cpu > self.cpu_high and delay > self.delay_high:
#             return "controller_overloaded", "CPU > threshold AND delay high"

#         if controller_heartbeat is False:
#             return "controller_crashed", "Controller heartbeat missing"

#         if pkt_in > 0.7 and delay > 0.7:
#             return "controller_slow", "High packet-in + high delay"

#         if rest_api_fail:
#             return "controller_module_failure", "REST API failure"

#         # ------------------------------
#         # SWITCH HEALTH RULES
#         # ------------------------------
#         if switch_disconnect and link_util < 0.3:
#             return "switch_disconnected", "Switch lost contact unexpectedly"

#         if switch_util > self.switch_port_util_high:
#             return "switch_overloaded", "Switch port utilization high"

#         if packet_loss > self.packet_loss_th:
#             return "switch_buffer_overflow", "Packet loss exceeds threshold"

#         # ------------------------------
#         # LINK HEALTH RULES
#         # ------------------------------
#         # ❗ No 'link_util == 0' false positives anymore
#         if link_util > self.link_util_high and delay > self.delay_high:
#             return "link_congestion", "High utilization + high delay"

#         if packet_loss > self.packet_loss_th:
#             return "link_quality_degraded", "Packet loss indicates degraded link"

#         # ------------------------------
#         # FLOW TABLE / DATA PLANE
#         # ------------------------------
#         if flow_table > self.flow_table_high:
#             return "flow_table_full", "Flow table > threshold"

#         if delay > self.delay_high and pkt_out < 0.2:
#             return "flow_install_delay", "High delay + low pkt_out"

#         # FIXED: Now only triggers when ML anomaly ALSO present
#         if (lstm_flag or if_flag) and flow_table < 0.1 and cpu < 0.4 and pkt_in < 0.2:
#             return "flow_drop_unexpected", "ML anomaly + sudden drop in flows"

#         # ------------------------------
#         # ML + METRIC COMBINATION RULES
#         # ------------------------------
#         if lstm_flag or if_flag:

#             if cpu > self.cpu_high:
#                 return "predicted_controller_overload", "ML + rising CPU"

#             if delay > self.delay_high:
#                 return "predicted_link_congestion", "ML + increasing delay"

#             if switch_disconnect:
#                 return "probable_controller_crash", "ML + switch disconnect"

#         # ------------------------------
#         # SPECIAL CASES
#         # ------------------------------
#         if pkt_in > 0.85:
#             return "packet_in_storm", "Packet-in spike detected"

#         if abs(flow_table - link_util) > 0.5:
#             return "state_inconsistency", "Flow table vs link utilization mismatch"

#         if rest_api_fail:
#             return "app_layer_error", "Northbound API error"

#         return "normal", "No anomaly detected"

#     # =========================================================
#     # 2. DECISION ENGINE
#     # =========================================================
#     def decide(self, root_cause):

#         table = {
#             "controller_overloaded": ("restart_controller_module", "Redistribute controller load"),
#             "controller_crashed": ("trigger_failover", "Switch to backup controller"),
#             "controller_slow": ("reduce_packet_in_rate", "Reduce incoming events"),
#             "controller_module_failure": ("restart_module", "Restart crashed component"),

#             "switch_disconnected": ("reconnect_switch", "Re-establish switch link"),
#             "switch_overloaded": ("reroute_traffic", "Balance load across switches"),
#             "switch_buffer_overflow": ("throttle_traffic", "Apply queue management"),

#             "link_congestion": ("load_balance", "Shift flows to alternate path"),
#             "link_quality_degraded": ("reroute_or_reduce_load", "Link poor → reroute or limit load"),

#             "flow_table_full": ("clear_old_flows", "Free TCAM space"),
#             "flow_install_delay": ("restart_flow_module", "Fix flow installation delay"),
#             "flow_drop_unexpected": ("restore_flows_backup", "Restore previous flow states"),

#             "predicted_controller_overload": ("preemptive_restart", "Prevent overload crash"),
#             "predicted_link_congestion": ("switch_path", "Avoid predicted congestion"),
#             "probable_controller_crash": ("trigger_failover", "Failover immediately"),

#             "packet_in_storm": ("enable_rate_limit", "Stop packet-in storm"),
#             "state_inconsistency": ("resync_state", "Synchronize controller with switch"),
#             "app_layer_error": ("restart_app", "Fix northbound application"),
#         }

#         return table.get(root_cause, ("no_action", "Everything normal"))

#     # =========================================================
#     # 3. MAIN PIPELINE
#     # =========================================================
#     def run(self, metrics):
#         root_cause, reason = self.diagnose(metrics)
#         action, why = self.decide(root_cause)
#         return {
#             "root_cause": root_cause,
#             "why_detected": reason,
#             "recommended_action": action,
#             "why_action": why
#         }

# ============================================================
# MODEL-DRIVEN DIAGNOSIS + DECISION ENGINE
# ============================================================

# ============================================================
# MODEL-DRIVEN DIAGNOSIS + DECISION ENGINE (WITH SEVERITY)
# ============================================================

class MLDecisionEngine:

    def __init__(self):
        # ---------------------------
        # Mapping: model reason → anomaly type
        # ---------------------------
        self.reason_to_type = {

            # LSTM / IF common interpretations
            "CPU spike / overload": "cpu_overload",
            "Memory leak or sudden increase": "memory_leak",
            "RTT spike / latency anomaly": "rtt_spike",
            "Packet-In burst / possible DoS": "packet_in_burst",
            "Controller broadcast spike": "controller_broadcast_spike",
            "Flow churn anomaly": "flow_churn_spike",
            "Bandwidth anomaly": "bandwidth_surge",

            # IF reason mappings
            "Flow table saturation": "flow_table_full",
            "High Bandwidth Surge": "bandwidth_surge",
            "CPU/Mem Overload": "cpu_overload",
            "Possible DoS / High Packet-In + Churn": "packet_in_burst",
            "RTT Spike / Link Degradation": "rtt_spike",
            "Controller Slow Response": "controller_slow",
            "Link Failure / Flap Detected": "link_failure", # ADDED MAPPING
        }

        # ---------------------------
        # Healing action + severity mapping
        # ---------------------------
        self.action_map = {
            "cpu_overload": ("scale_controller_resources",
                             "High CPU deviation detected",
                             "HIGH"),

            "memory_leak": ("restart_module",
                            "Memory usage deviated abnormally",
                            "HIGH"),

            "rtt_spike": ("reroute_traffic",
                          "High RTT / latency anomaly",
                          "MEDIUM"),
            
            "link_failure": ("reroute_traffic",
                             "Link Failure confirmed by Port Status",
                             "CRITICAL"),

            "packet_in_burst": ("enable_rate_limit",
                                "Packet-In deviation suggests DoS/spike",
                                "CRITICAL"),

            "controller_broadcast_spike": ("optimize_flow_rules",
                                           "Abnormal Packet-Out pattern",
                                           "MEDIUM"),

            "flow_churn_spike": ("rebalance_flows",
                                 "Flow churn anomaly detected",
                                 "MEDIUM"),

            "bandwidth_surge": ("load_balance",
                                "Sudden bandwidth increase/decrease",
                                "MEDIUM"),

            "flow_table_full": ("clear_old_flows",
                                "Flow table saturation detected",
                                "CRITICAL"),

            "controller_slow": ("restart_flow_module",
                                "Controller slow to respond",
                                "HIGH"),

            "general_outlier": ("monitor",
                                 "Unclassified anomaly detected",
                                 "LOW"),

            "normal": ("no_action",
                       "No anomaly detected",
                       "LOW")
        }

    # --------------------------------------------------------------------
    # Extract final anomaly type
    # --------------------------------------------------------------------
    def classify_anomaly(self, lstm_reasons, if_reasons):

        combined = lstm_reasons + if_reasons
        if not combined:
            return "normal", "No deviation detected"

        # 1. Map all raw reasons to standardized types
        detected_types = []
        for r in combined:
            if r in self.reason_to_type:
                detected_types.append(self.reason_to_type[r])
        
        # 2. Strict Priority Check (Critical First)
        # We check for specific Critical types regardless of list order
        
        if "packet_in_burst" in detected_types:
            return "packet_in_burst", "DoS Attack detected (High Packet-In)"
            
        if "link_failure" in detected_types:
            return "link_failure", "Link Failure / Flap Detected"

        if "rtt_spike" in detected_types and "bandwidth_surge" in detected_types:
             # Often implies Link Failure or Congestion
             return "rtt_spike", "Latency spike detected"
             
        if "cpu_overload" in detected_types:
            return "cpu_overload", "CPU Overload detected"
            
        # 3. Fallback to list order (highest Z-score)
        for r in combined:
            if r in self.reason_to_type:
                return self.reason_to_type[r], r

        return "general_outlier", combined[0]

    # --------------------------------------------------------------------
    # Main decision engine
    # --------------------------------------------------------------------
    def run(self, lstm_output, if_output):

        lstm_flag = lstm_output.get("lstm_anomaly", False)
        if_flag = if_output.get("if_anomaly", False)

        # CASE 1 — No anomaly detected
        if not lstm_flag and not if_flag:
            return {
                "anomaly": False,
                "type": "normal",
                "why": "Both models report normal behavior",
                "healing_action": "no_action",
                "why_action": "No anomaly detected",
                "severity": "LOW"
            }

        lstm_reasons = lstm_output.get("reasons", [])
        if_reasons = if_output.get("reasons", [])

        # Determine anomaly type from explanations
        anomaly_type, matched_reason = self.classify_anomaly(lstm_reasons, if_reasons)

        # Fetch action + explanation + severity
        action, why_action, severity = self.action_map.get(
            anomaly_type,
            ("monitor", "Unclassified anomaly", "LOW")
        )

        full_reason = f"LSTM reasons: {lstm_reasons} | IF reasons: {if_reasons}"

        return {
            "anomaly": True,
            "type": anomaly_type,
            "matched_reason": matched_reason,
            "why": full_reason,
            "healing_action": action,
            "why_action": why_action,
            "severity": severity
        }

