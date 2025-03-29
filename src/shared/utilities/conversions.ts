const convertMinuteToMilleSeconds = (min: number) => {
  return min * 60 * 1000;
};

const convertSecondToMilleSeconds = (sec: number) => {
  return sec * 1000;
};

export { convertMinuteToMilleSeconds, convertSecondToMilleSeconds };
