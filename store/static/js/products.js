const priceRange = document.getElementById('min_price')
const priceRangeOutput = document.querySelector(".form-range-output[for='min_price']")

priceRange.addEventListener('input', function () {
    priceRangeOutput.value = priceRange.value
});

const maxpriceRange = document.getElementById('max_price')
const maxpriceRangeOutput = document.querySelector(".form-range-output[for='max_price']")

maxpriceRange.addEventListener('input', function () {
    maxpriceRangeOutput.value = maxpriceRange.value
});
