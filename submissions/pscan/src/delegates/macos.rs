use crate::{ProcessScanner, ScannerDelegate};
use clap::builder::styling::{AnsiColor, Effects, Styles};
use libc::{RTLD_LAZY, c_int, c_void, dlopen, dlsym, getuid, pid_t, size_t, sysctlbyname};
use mach2::{
    kern_return::KERN_SUCCESS,
    port::mach_port_t,
    traps::{mach_task_self, task_for_pid},
    vm::mach_vm_region,
    vm_region::{VM_REGION_BASIC_INFO, vm_region_submap_info},
    vm_types::mach_vm_address_t,
};
use psutil::process::Process;
use std::{error::Error, ffi::CString, mem::size_of, ptr::addr_of_mut};

unsafe extern "C" {
    unsafe fn csops(pid: i32, ops: u32, useraddr: *mut c_void, usersize: size_t) -> c_int;
}

fn get_task_name(pid: u32) -> Result<String, Box<dyn Error>> {
    Process::new(pid)?.name().map_err(|e| e.into())
}

fn get_native_system_architecture() -> Result<String, Box<dyn Error>> {
    let mut arm64_support: i32 = 0;
    let mut arm64_size = size_of::<i32>();

    if unsafe {
        sysctlbyname(
            CString::new("hw.optional.arm64")?.as_ptr(),
            &mut arm64_support as *mut i32 as *mut c_void,
            &mut arm64_size,
            std::ptr::null_mut(),
            0,
        )
    } == 0
        && arm64_support == 1
    {
        return Ok("arm64".to_string());
    }

    let mut size = 0;
    unsafe {
        sysctlbyname(
            CString::new("hw.machine")?.as_ptr(),
            std::ptr::null_mut(),
            &mut size,
            std::ptr::null_mut(),
            0,
        );
    }

    if size > 0 {
        let mut buffer = vec![0u8; size];
        if unsafe {
            sysctlbyname(
                CString::new("hw.machine")?.as_ptr(),
                buffer.as_mut_ptr() as *mut c_void,
                &mut size,
                std::ptr::null_mut(),
                0,
            )
        } == 0
        {
            if buffer[size - 1] == 0 {
                buffer.truncate(size - 1);
            }
            return String::from_utf8(buffer)
                .map_err(|_| "Invalid UTF-8 in machine architecture".into());
        }
    }

    Err("Failed to get system architecture".into())
}

fn get_process_translation_status(pid: u32) -> Result<bool, Box<dyn Error>> {
    unsafe {
        let lib_path = CString::new("/usr/lib/liboah.dylib")?;
        let handle = dlopen(lib_path.as_ptr(), RTLD_LAZY);
        if handle.is_null() {
            return Err("Failed to load liboah.dylib".into());
        }

        let func_name = CString::new("oah_is_process_translated")?;
        let func_ptr = dlsym(handle, func_name.as_ptr());
        if func_ptr.is_null() {
            return Err("Failed to find oah_is_process_translated symbol".into());
        }

        let oah_is_process_translated: extern "C" fn(pid_t) -> bool = std::mem::transmute(func_ptr);
        Ok(oah_is_process_translated(pid as pid_t))
    }
}

fn get_process_architecture(pid: u32) -> Result<String, Box<dyn Error>> {
    if get_process_translation_status(pid)? {
        return Ok("x86_64".to_string());
    }

    get_native_system_architecture()
}

fn check_hardened_runtime(pid: u32) -> Result<bool, Box<dyn Error>> {
    let mut flags: u32 = 0;
    if unsafe {
        csops(
            pid as i32,
            0,
            &mut flags as *mut u32 as *mut c_void,
            size_of::<u32>(),
        )
    } == 0
    {
        return Ok((flags & 0x00010000) != 0);
    }
    Err("Failed to get code signing status".into())
}

enum BaseAddressResult {
    Success(u64),
    HardenedRuntime,
    NoRootPrivilege,
    TaskForPidFailed,
    RegionFailed,
}

fn get_base_address(pid: u32, hardened: bool) -> BaseAddressResult {
    if hardened {
        return BaseAddressResult::HardenedRuntime;
    }

    if unsafe { getuid() } != 0 {
        return BaseAddressResult::NoRootPrivilege;
    }

    unsafe {
        let mut task: mach_port_t = 0;
        let kr = task_for_pid(mach_task_self(), pid as i32, &mut task);

        if kr != KERN_SUCCESS {
            return BaseAddressResult::TaskForPidFailed;
        }

        let mut region: vm_region_submap_info = vm_region_submap_info::default();
        let mut address: mach_vm_address_t = 0;
        let mut size: u64 = 0;
        let mut object_name: u32 = 0;

        let kr = mach_vm_region(
            task,
            addr_of_mut!(address),
            addr_of_mut!(size),
            VM_REGION_BASIC_INFO,
            addr_of_mut!(region) as _,
            &mut (size_of::<vm_region_submap_info>() as u32),
            addr_of_mut!(object_name),
        );

        if kr != KERN_SUCCESS {
            return BaseAddressResult::RegionFailed;
        }

        BaseAddressResult::Success(address)
    }
}

impl ProcessScanner for ScannerDelegate {
    fn scan(&self, pid: u32) -> Result<(), Box<dyn Error>> {
        let name = get_task_name(pid)?;
        let arch = get_process_architecture(pid)?;
        let translated = get_process_translation_status(pid)?;
        let hardened = check_hardened_runtime(pid)?;
        let base_address_result = get_base_address(pid, hardened);

        let styles = Styles::styled()
            .header(AnsiColor::Blue.on_default() | Effects::BOLD)
            .literal(AnsiColor::White.on_default())
            .valid(AnsiColor::Green.on_default())
            .invalid(AnsiColor::Red.on_default());

        let pipe_style = styles.get_header();
        let white_style = styles.get_literal();
        let green_style = styles.get_valid();
        let red_style = styles.get_invalid();

        match &base_address_result {
            BaseAddressResult::HardenedRuntime => {
                println!(
                    "WARNING: Hardened Runtime disallows the application from getting the base address."
                );
            }
            BaseAddressResult::NoRootPrivilege => {
                println!(
                    "WARNING: Base address unavailable due to lack of root privilege. task_for_pid failed."
                );
            }
            BaseAddressResult::TaskForPidFailed | BaseAddressResult::RegionFailed => {
                println!(
                    "WARNING: Could not get base address. Is the target application arm64e / a system application?"
                );
            }
            _ => {}
        }

        fn print_border(style: &clap::builder::styling::Style, content: &str) {
            println!("{}{}{}", style.render(), content, style.render_reset());
        }

        fn print_row(
            pipe_style: &clap::builder::styling::Style,
            value_style: &clap::builder::styling::Style,
            label: &str,
            value: &str,
        ) {
            print!("{}{}", pipe_style.render(), "│ ");
            print!("{:<19}", label);
            print!(" {}", pipe_style.render());
            print!("│ {}", value_style.render());
            print!("{:<36}", value);
            print!(
                "{} {}│{}",
                value_style.render_reset(),
                pipe_style.render(),
                pipe_style.render_reset()
            );
            println!();
        }

        print_border(
            &pipe_style,
            "┌─────────────────────┬──────────────────────────────────────┐",
        );
        print_border(
            &pipe_style,
            "│ Property            │ Value                                │",
        );
        print_border(
            &pipe_style,
            "├─────────────────────┼──────────────────────────────────────┤",
        );
        print_row(&pipe_style, &white_style, "Task Name", &name);
        print_row(&pipe_style, &white_style, "Architecture", &arch);
        print_row(
            &pipe_style,
            if hardened { &green_style } else { &red_style },
            "Hardened Runtime",
            &hardened.to_string(),
        );
        print_row(
            &pipe_style,
            if translated { &green_style } else { &red_style },
            "Rosetta Translated",
            &translated.to_string(),
        );

        let base_address_value = match base_address_result {
            BaseAddressResult::Success(addr) => format!("0x{:016x}", addr),
            _ => "N/A".to_string(),
        };
        let base_address_style = match base_address_result {
            BaseAddressResult::Success(_) => &white_style,
            _ => &red_style,
        };
        print_row(
            &pipe_style,
            base_address_style,
            "Base Address",
            &base_address_value,
        );

        print_border(
            &pipe_style,
            "└─────────────────────┴──────────────────────────────────────┘",
        );

        Ok(())
    }
}
