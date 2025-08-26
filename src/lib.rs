use indicatif::{ParallelProgressIterator, ProgressBar, ProgressStyle};
use pyo3::prelude::*;
use rayon::prelude::*;

fn rho_elt_process(
    rho_a_i: &String,
    rho_b_i: &String,
    rho_a_i1: &String,
    rho_b_i1: &String,
) -> f64 {
    if rho_a_i != rho_b_i {
        0.5
    } else {
        if rho_a_i1 == rho_b_i1 {
            5.0
        } else {
            -4.0
        }
    }
}

fn get_trace(rho_a: &Vec<String>, rho_b: &Vec<String>, substring_index: &Vec<usize>) -> f64 {
    if substring_index.is_empty() {
        return 1.0;
    }

    substring_index.iter().fold(1.0, |acc, &i| {
        acc * rho_elt_process(&rho_a[i], &rho_b[i], &rho_a[i + 1], &rho_b[i + 1])
    })
}

#[pyfunction]
fn perform_trace_calculation(data: Vec<Vec<String>>, subs: Vec<usize>) -> f64 {
    let num_samples = data.len();
    let substring_indices: Vec<usize> = subs.iter().map(|&i| i * 2).collect();

    let bar = ProgressBar::new(num_samples as u64);
    bar.set_style(
        ProgressStyle::default_bar()
            .template(
                "{spinner:.green} [{elapsed_precise}] [{bar:40.cyan/blue}] {pos}/{len} ({eta})",
            )
            .unwrap()
            .progress_chars("#>-"),
    );

    let result = (0..num_samples)
        .into_par_iter()
        .progress_with(bar)
        .map(|i| {
            let row_sum: f64 = (i + 1..num_samples)
                .into_par_iter()
                .map(|j| get_trace(&data[i], &data[j], &substring_indices))
                .sum();
            row_sum
        })
        .sum();

    result
}

/// A Python module implemented in Rust.
#[pymodule]
fn shadow_trace_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(perform_trace_calculation, m)?)?;
    Ok(())
}
