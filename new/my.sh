#!/bin/bash

run_my_test() 
 { 
echo "test"
}
 
run_my_test

#adb shell "dumpsys display | grep mScreenState"
mScreenState() {
echo "--- status (mScreenState) ---"
adb shell "dumpsys display | grep mScreenState"
local status=$?
echo "--- exit code: $status ---"
return "$status"
} 

#adb shell "dumpsys power | grep -E 'PARTIAL_WAKE_LOCK.*termuxnano'"
wake_lock() {
echo "--- status (wake-lock) ---"
adb shell "dumpsys power | grep -E 'PARTIAL_WAKE_LOCK.*termuxnano'"
local status=$?
echo "--- exit code: $status ---"
return "$status"
}

#adb shell "input keyevent 224 && input swipe 540 1500 540 500 500 && input text seal && input keyevent 66" 
# 224  это цифровой код клавиши KEYCODE_WAKEUP.
# 66  это цифровой код клавиши KEYCODE_ENTER
in_block() {
echo "--- in-block tablet ---"
adb shell "input keyevent 224 && input swipe 540 1500 540 500 500 && input text seal && input keyevent 66"
local status=$?
echo "--- exit code: $status ---"
return "$status"
}

put_to_sleep() { 
adb shell "input keyevent 26" 
sleep 2
}

#adb shell "dumpsys display | grep mScreenState"
#adb shell dumpsys power | grep -E "PARTIAL_WAKE_LOCK.*termuxnano
#adb shell "input keyevent 224 && input swipe 540 1500 540 500 500 && input text seal && input keyevent 66"

# ---  основной цикл скрипта
echo "---- Start. -----"

termux-wake-lock

for i in {1..3}; do
 echo "Cycle $i"
 wake_lock
 put_to_sleep
 sleep 180 
 in_block
done

# Снимаем блокировку сна, чтобы устройство могло нормально засыпать в будущем
termux-wake-unlock

echo "---- Done. -----"
