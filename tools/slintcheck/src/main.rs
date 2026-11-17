// 离线 Slint 语法校验器。
// 逐个把 .slint 文件交给 slint-interpreter 的编译器，输出 JSON 结果。
// 用法：slintcheck [--include DIR]... FILE.slint ...
// 输出：每行一个 JSON 对象 {"path":..., "ok":true/false, "errors":[...], "warnings":[...]}
//
// 注意：这是语法/类型层面的编译校验，不会打开窗口，也不执行任何界面逻辑。

use slint_interpreter::{Compiler, DiagnosticLevel};
use std::path::PathBuf;

fn main() {
    let mut includes: Vec<PathBuf> = vec![];
    let mut files: Vec<PathBuf> = vec![];
    let mut args = std::env::args().skip(1);
    while let Some(a) = args.next() {
        if a == "--include" {
            if let Some(v) = args.next() {
                includes.push(PathBuf::from(v));
            }
        } else {
            files.push(PathBuf::from(a));
        }
    }

    for path in files {
        let mut compiler = Compiler::default();
        let mut inc = includes.clone();
        if let Some(parent) = path.parent() {
            inc.push(parent.to_path_buf());
        }
        compiler.set_include_paths(inc);

        let result = spin_on::spin_on(compiler.build_from_path(&path));
        let mut errors = vec![];
        let mut warnings = vec![];
        for d in result.diagnostics() {
            let (line, col) = d.line_column();
            let msg = format!("{}:{}: {}", line, col, d.message());
            match d.level() {
                DiagnosticLevel::Error => errors.push(msg),
                _ => warnings.push(msg),
            }
        }
        let names: Vec<String> = result.component_names().map(|s| s.to_string()).collect();
        println!(
            "{}",
            serde_json_like(&path.display().to_string(), errors.is_empty(), &errors, &warnings, &names)
        );
    }
}

// 不引入 serde，手工拼一个最小 JSON，避免额外依赖。
fn esc(s: &str) -> String {
    s.replace('\\', "\\\\")
        .replace('"', "\\\"")
        .replace('\n', "\\n")
        .replace('\r', "\\r")
        .replace('\t', "\\t")
}

fn arr(v: &[String]) -> String {
    let inner: Vec<String> = v.iter().map(|s| format!("\"{}\"", esc(s))).collect();
    format!("[{}]", inner.join(","))
}

fn serde_json_like(
    path: &str,
    ok: bool,
    errors: &[String],
    warnings: &[String],
    names: &[String],
) -> String {
    format!(
        "{{\"path\":\"{}\",\"ok\":{},\"errors\":{},\"warnings\":{},\"components\":{}}}",
        esc(path),
        if ok { "true" } else { "false" },
        arr(errors),
        arr(warnings),
        arr(names)
    )
}
