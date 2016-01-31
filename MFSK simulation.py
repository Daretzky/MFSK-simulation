#-*- coding: utf-8 -*-
__author__ = u'Dariusz Słowikowski'
import cmath
import numpy
import numpy.fft
import numpy.random
import pylab


class Generator(object):
    def __init__(self, message, frequency, impulse_length):
        self.message = message
        self.frequency = frequency * 1000
        self.impulse_length = impulse_length / 1000
        self.sampling_frequency = self.frequency * 8

        dt = self.frequency / 100
        self.frequency2 = self.frequency + 5*dt
        self.frequency3 = self.frequency + 10*dt
        self.frequency4 = self.frequency + 15*dt

    freq1 = []
    freq2 = []
    freq3 = []
    freq4 = []
    asciiVector = []
    binVector = []
    message_vector = numpy.array([])
    time_segment = []
    signal_length = 0
    vector = numpy.array([])

    def parity_check(self, char):
        count = 0
        for y in bin(ord(char)):
            if y == "1":
                count += 1
        if count % 2 == 0:
            return "0"
        elif count % 2 != 0:
            return "1"

    def stringToBin(self):
        s = ""
        for char in self.message:
            parity_bit = self.parity_check(char)
            bin_char = str((bin(ord(char))[2:])).zfill(7) + str(parity_bit)
            self.binVector.append(bin_char)
        for y in self.binVector:
            s += y
        return s
    """
    code alphabet:
    f1 = 00
    f2 - 01
    f3 - 10
    f4 - 11
    """
    def generate(self):
        number = int(self.sampling_frequency * self.impulse_length)
        self.time_segment = [float(n) / self.sampling_frequency for n in range(number)]

        #Generating 4 sinusoids with different frequencies
        self.freq1 = [cmath.rect(1.0, 2 * cmath.pi * t * self.frequency) for t in self.time_segment]
        self.freq1 = numpy.array(self.freq1)
        self.freq2 = [cmath.rect(1.0, 2 * cmath.pi * t * self.frequency2) for t in self.time_segment]
        self.freq2 = numpy.array(self.freq2)
        self.freq3 = [cmath.rect(1.0, 2 * cmath.pi * t * self.frequency3) for t in self.time_segment]
        self.freq3 = numpy.array(self.freq3)
        self.freq4 = [cmath.rect(1.0, 2 * cmath.pi * t * self.frequency4) for t in self.time_segment]
        self.freq4 = numpy.array(self.freq4)

    def encode(self, message):
        for x in range(1, len(message), 2):
            if message[x-1] + message[x] == "00":
                self.vector = numpy.hstack([self.vector, self.freq1])
            elif message[x-1] + message[x] == "01":
                self.vector = numpy.hstack([self.vector, self.freq2])
            elif message[x-1] + message[x] == "10":
                self.vector = numpy.hstack([self.vector, self.freq3])
            elif message[x-1] + message[x] == "11":
                self.vector = numpy.hstack([self.vector, self.freq4])
            self.signal_length += 1
        return self.vector


class Decoder(object):
    def receiving(self, y):
        received = ''

        for x in range(0, len(y), len(generator.time_segment)):
            segment = y[x: x+len(generator.time_segment)]
            fft_segment = numpy.fft.fft(segment*numpy.blackman(len(segment)))
            fft_segment /= max(abs(fft_segment))
            freqs = numpy.fft.fftfreq(fft_segment.size, d=1 / generator.sampling_frequency)
            peak_value_index = numpy.argmax(fft_segment[0:fft_segment.size / 4])
            """
            code alphabet:
            f1 = 00
            f2 - 01
            f3 - 10
            f4 - 11
            """
            if freqs[peak_value_index] == generator.frequency:
                received += "00"
            elif freqs[peak_value_index] == generator.frequency2:
                received += "01"
            elif freqs[peak_value_index] == generator.frequency3:
                received += "10"
            elif freqs[peak_value_index] == generator.frequency4:
                received += "11"
        return received

    def decoding(self, bin_message):
        charsb = []
        error = False

        for bit in range(0, len(bin_message), 8):
            charsb.append(bin_message[bit:bit+8])

        message_received = ""
        for char in charsb:
            count = 0
            for bit in char:
                if bit == '1':
                    count += 1
            if count % 2 != 0:
                error = True
            else:
                message_received += chr(int("0b" + str(char[: 7]), 2))
        if len(message_received) != 5:
                error = True
        params = (message_received, error)
        return params

print "\nSIMULATION OF TRANSMISSION SYSTEM WITH SINUSOIDAL IMPULSES MFSK AND PARITY CHECK\n\n"

# Loadin input
print "Provide data input"

message = ""

while len(message) != 5:
    message = str(raw_input('Write 5 letter message: \n'))

while True:
    try:
        frequency = float(raw_input("Choose frequency [kHz]: \n"))
        break
    except ValueError:
        print "ERROR: wrong value."

while True:
    try:
        impulse_length = float(raw_input("Provide impulse lenght [ms]: \n"))
        break
    except ValueError:
        print "ERROR: wrong value."

while True:
    try:
        SNR = float(raw_input("Set Signal to Noise ratio [dB]: \n"))
        break
    except ValueError:
        print "ERROR: wrong value."


# Transmission simulation
generator = Generator(message, frequency, impulse_length)  # initialization of generator parameters
generator.generate()    # generation of MFSK impulses

message = generator.stringToBin()   # encoding message to binary value
s0 = generator.encode(message)      # encoding binary message with MFSK impulses

# Generator output
Timeline = [float(n) / generator.sampling_frequency for n in range(len(s0.real))]

pylab.plot(Timeline[:len(generator.time_segment * 3)], s0.real[:len(generator.time_segment * 3)])
pylab.xlabel("Timeline")
pylab.ylabel("Amplitudr")
pylab.title("Transmitter output")
pylab.show()

# spectrum analysis - transmitter

spectrum_transmitter = numpy.fft.fftshift(numpy.fft.fft(s0*numpy.blackman((len(s0.real)))))
spectrum_transmitter = spectrum_transmitter/max(abs(spectrum_transmitter))  # normalisation
freqline = numpy.arange(-generator.sampling_frequency / 2, generator.sampling_frequency / 2,
                        generator.sampling_frequency / len(spectrum_transmitter))
pylab.plot(freqline, 20*numpy.log10(abs(spectrum_transmitter)))
pylab.xlabel("Frequency")
pylab.ylabel("E")
pylab.title("Spectrum - transmitter output")
pylab.show()

# AWGN channel

noise_length = len(s0)
average = numpy.mean(s0)
var = sum(abs(s0 - average)**2) / noise_length
sigma = numpy.sqrt(var/2)*10**(-SNR/20)

Noise = numpy.random.normal(loc=0.0, scale=sigma, size=(noise_length, 2))
s1 = [s + complex(*n) for s, n in zip(s0.real, Noise)]

print("Assumed SNR:", SNR)
signal_enery = sum(abs(s0) ** 2)
noise_enery = sum(k ** 2 for n in Noise for k in n)
print("Obtained SNR:", 10 * numpy.log10(signal_enery / noise_enery))

pylab.plot(Timeline, s1)
pylab.xlabel("Timeline")
pylab.ylabel("Amplitude")
pylab.title("Transmitted signal with white noise")
pylab.show()

# detector FFT

received_binary = Decoder().receiving(s1)
decoded_message = Decoder().decoding(received_binary)

if not decoded_message[1]:
    print "Received message: %s" % decoded_message[0]
elif decoded_message[1]:
    print "ERROR: Received: %s" % decoded_message[0]


