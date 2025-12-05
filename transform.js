// Function that deeply merges two objects, with second object values taking precedence
function deepMerge(obj1, obj2) {
    for (const key in obj2) {
        if (obj2.hasOwnProperty(key)) {
            if (obj1[key] && typeof obj1[key] === 'object' && typeof obj2[key] === 'object') {
                obj1[key] = deepMerge(obj1[key], obj2[key]);
            } else {
                obj1[key] = obj2[key];
            }
        }
    }
    return obj1;
}

module.exports = { deepMerge };